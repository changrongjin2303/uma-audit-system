"""
市场信息价材料分析服务

用于分析项目中已匹配材料与市场信息价材料库中价格的差异
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
import logging
from decimal import Decimal, ROUND_HALF_UP
import asyncio

from app.models.project import ProjectMaterial
from app.models.material import BaseMaterial
from app.models.analysis import PriceAnalysis, AnalysisStatus
from app.utils.unit_conversion import (
    normalize_unit,
    can_convert_units,
    get_conversion_factor,
    convert_unit_price,
)

logger = logging.getLogger(__name__)


class PricedMaterialAnalysisService:
    """市场信息价材料分析服务"""
    
    def __init__(self):
        self.price_threshold = Decimal('0.05')  # 5%的价格差异阈值
        
    async def analyze_priced_materials(
        self,
        db: AsyncSession,
        project_id: int,
        material_ids: Optional[List[int]] = None,
        batch_size: int = 10
    ) -> Dict[str, Any]:
        """
        分析市场信息价材料价格差异
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            material_ids: 要分析的材料ID列表，如果为空则分析所有已匹配的材料
            batch_size: 批量处理大小
            
        Returns:
            分析结果字典
        """
        # 如果没有提供材料ID，则获取所有已匹配的材料ID
        if not material_ids:
            logger.info(f"未提供材料ID，将获取项目 {project_id} 所有已匹配的材料")
            stmt = select(ProjectMaterial.id).where(
                and_(
                    ProjectMaterial.project_id == project_id,
                    ProjectMaterial.is_matched == True,
                    ProjectMaterial.matched_material_id.isnot(None)
                )
            )
            result = await db.execute(stmt)
            material_ids = list(result.scalars().all())
            
        logger.info(f"开始分析项目 {project_id} 的市场信息价材料价格差异，材料数量: {len(material_ids)}")
        
        analyzed_count = 0
        differences = []
        
        # 分批处理材料
        for i in range(0, len(material_ids), batch_size):
            batch = material_ids[i:i + batch_size]
            logger.info(f"处理批次 {i // batch_size + 1}，材料ID: {batch}")
            
            batch_differences = await self._analyze_material_batch(db, project_id, batch)
            differences.extend(batch_differences)
            analyzed_count += len(batch)
            
            # 避免过度频繁的数据库操作
            if i + batch_size < len(material_ids):
                await asyncio.sleep(0.1)
        
        # 统计差异数量
        differences_count = len([d for d in differences if d['has_difference']])
        
        # 保存分析结果到数据库
        await self._save_analysis_results(db, differences)
        
        result = {
            "analyzed_count": analyzed_count,
            "differences_count": differences_count,
            "differences": differences,
            "summary": await self._generate_summary(differences)
        }
        
        logger.info(f"市场信息价材料分析完成，分析了 {analyzed_count} 个材料，发现 {differences_count} 个差异")
        return result
    
    async def _analyze_material_batch(
        self,
        db: AsyncSession,
        project_id: int,
        material_ids: List[int]
    ) -> List[Dict[str, Any]]:
        """分析一批材料的价格差异"""
        
        contract_info = await self._get_project_contract_info(db, project_id)
        
        # 获取项目材料及其匹配的基准材料信息
        stmt = select(
            ProjectMaterial.id,
            ProjectMaterial.material_name,
            ProjectMaterial.specification,
            ProjectMaterial.unit,
            ProjectMaterial.quantity,
            ProjectMaterial.unit_price.label('project_unit_price'),
            ProjectMaterial.serial_number,
            ProjectMaterial.notes,
            ProjectMaterial.matched_material_id,
            BaseMaterial.id.label('base_material_id'),
            BaseMaterial.name.label('base_material_name'),
            BaseMaterial.specification.label('base_specification'),
            BaseMaterial.unit.label('base_unit'),
            BaseMaterial.price_including_tax.label('base_price_including_tax'),
            BaseMaterial.price_excluding_tax.label('base_price_excluding_tax'),
            BaseMaterial.material_code.label('base_material_code'),
            BaseMaterial.category_id,
            BaseMaterial.price_type.label('source_type'),
            BaseMaterial.price_date.label('year_month'),
            BaseMaterial.region
        ).select_from(
            ProjectMaterial.__table__.join(
                BaseMaterial, ProjectMaterial.matched_material_id == BaseMaterial.id
            )
        ).where(
            and_(
                ProjectMaterial.project_id == project_id,
                ProjectMaterial.id.in_(material_ids),
                ProjectMaterial.is_matched == True,
                ProjectMaterial.matched_material_id.isnot(None)
            )
        )
        
        result = await db.execute(stmt)
        materials = result.all()
        
        differences = []
        
        for material in materials:
            try:
                analysis = await self._analyze_single_material(
                    material,
                    contract_info=contract_info,
                    db=db
                )
                differences.append(analysis)
            except Exception as e:
                logger.error(f"分析材料 {material.id} 时出错: {str(e)}")
                # 创建错误记录
                differences.append({
                    "material_id": material.id,
                    "material_name": material.material_name,
                    "error": str(e),
                    "has_difference": False,
                    "analysis_status": "failed"
                })
        
        return differences

    async def _get_project_contract_info(self, db: AsyncSession, project_id: int) -> Dict[str, Optional[str]]:
        from app.models.project import Project
        stmt = select(
            Project.base_price_date,
            Project.price_base_date,
            Project.contract_start_date,
            Project.contract_end_date
        ).where(Project.id == project_id)
        result = await db.execute(stmt)
        project = result.first()
        
        if not project:
            return {
                "base_price_date": None,
                "contract_start_date": None,
                "contract_end_date": None
            }
        
        base_price = project.base_price_date or project.price_base_date
        
        return {
            "base_price_date": self._normalize_year_month(base_price),
            "contract_start_date": self._normalize_year_month(project.contract_start_date),
            "contract_end_date": self._normalize_year_month(project.contract_end_date)
        }
    
    def _normalize_year_month(self, value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        str_value = str(value).strip()
        if not str_value:
            return None
        str_value = str_value.replace('年', '-').replace('月', '')
        for sep in ['-', '/', '.']:
            if sep in str_value:
                parts = [p for p in str_value.split(sep) if p]
                break
        else:
            if len(str_value) == 6 and str_value.isdigit():
                parts = [str_value[:4], str_value[4:]]
            else:
                parts = [str_value[:4], str_value[4:]] if len(str_value) > 4 else [str_value, '1']
        if len(parts) < 2:
            return None
        try:
            year = int(parts[0])
            month = int(parts[1])
        except ValueError:
            return None
        month = max(1, min(month, 12))
        return f"{year:04d}-{month:02d}"
    
    def _year_month_tuple(self, value: Optional[str]) -> Optional[Tuple[int, int]]:
        norm = self._normalize_year_month(value)
        if not norm:
            return None
        parts = norm.split('-')
        if len(parts) != 2:
            return None
        try:
            return int(parts[0]), int(parts[1])
        except ValueError:
            return None
    
    def _is_within_contract(self, price_date: Optional[str], contract_info: Dict[str, Optional[str]]) -> bool:
        ym_tuple = self._year_month_tuple(price_date)
        if not ym_tuple:
            return False
        start_tuple = self._year_month_tuple(contract_info.get("contract_start_date"))
        end_tuple = self._year_month_tuple(contract_info.get("contract_end_date"))
        if start_tuple and ym_tuple < start_tuple:
            return False
        if end_tuple and ym_tuple > end_tuple:
            return False
        return True
    
    async def _get_contract_period_prices(
        self,
        db: AsyncSession,
        material_row,
        contract_info: Dict[str, Optional[str]]
    ) -> List[BaseMaterial]:
        base_material = None
        if material_row.base_material_id:
            base_material = await db.get(BaseMaterial, material_row.base_material_id)
        if not base_material:
            return []
        
        conditions = []
        if base_material.material_code:
            conditions.append(BaseMaterial.material_code == base_material.material_code)
        else:
            conditions.append(BaseMaterial.name == base_material.name)
            if base_material.specification:
                conditions.append(BaseMaterial.specification == base_material.specification)
            else:
                conditions.append(
                    or_(
                        BaseMaterial.specification.is_(None),
                        BaseMaterial.specification == ""
                    )
                )
            if base_material.unit:
                conditions.append(BaseMaterial.unit == base_material.unit)
            if base_material.region:
                conditions.append(BaseMaterial.region == base_material.region)
            elif getattr(base_material, 'province', None):
                conditions.append(BaseMaterial.province == base_material.province)
            if base_material.price_type:
                conditions.append(BaseMaterial.price_type == base_material.price_type)
        
        stmt = select(BaseMaterial).where(and_(*conditions))
        result = await db.execute(stmt)
        materials = result.scalars().all()
        
        if not materials:
            materials = [base_material]
        
        contract_prices = [
            m for m in materials
            if self._is_within_contract(m.price_date, contract_info)
        ]
        
        if not contract_prices:
            contract_prices = materials
        
        return contract_prices
    
    async def _analyze_single_material(self, material, contract_info=None, db=None) -> Dict[str, Any]:
        """分析单个材料的价格差异"""
        
        # 获取价格数据
        project_price = Decimal(str(material.project_unit_price or 0))
        base_price_including_tax = Decimal(str(material.base_price_including_tax or 0))
        base_price_excluding_tax = Decimal(str(material.base_price_excluding_tax or 0))
        quantity = Decimal(str(material.quantity or 0))

        # 强制使用不含税价格进行计算
        base_price = base_price_excluding_tax

        original_base_price_including_tax = base_price_including_tax
        original_base_price_excluding_tax = base_price_excluding_tax

        # 单位换算处理
        project_unit_raw = material.unit or ""
        base_unit_raw = material.base_unit or ""
        project_unit = normalize_unit(project_unit_raw)
        base_unit = normalize_unit(base_unit_raw)

        conversion_factor = Decimal("1")
        conversion_applied = False

        if base_unit and project_unit and base_unit != project_unit:
            if can_convert_units(base_unit, project_unit):
                factor = get_conversion_factor(base_unit, project_unit)
                if factor is None:
                    raise ValueError(
                        f"材料 {material.material_name} 的单位无法换算: 项目单位 {project_unit_raw}, 基准单位 {base_unit_raw}"
                    )
                conversion_applied = True
                conversion_factor = factor
                # 将“每 base_unit 的价格”换算为“每 project_unit 的价格”，应当除以换算系数
                converted_excl = convert_unit_price(base_price, base_unit, project_unit)
                converted_incl = convert_unit_price(base_price_including_tax, base_unit, project_unit)
                if converted_excl is None or converted_incl is None:
                    raise ValueError(
                        f"材料 {material.material_name} 的单位换算失败: 项目单位 {project_unit_raw}, 基准单位 {base_unit_raw}"
                    )
                base_price = converted_excl.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
                base_price_including_tax = converted_incl.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
                base_price_excluding_tax = base_price
            else:
                raise ValueError(
                    f"材料 {material.material_name} 的单位不一致且无法换算: 项目单位 {project_unit_raw}, 基准单位 {base_unit_raw}"
                )

        # 如果不含税价格为0或不存在，则跳过这个材料的分析
        if base_price <= 0:
            raise ValueError(
                f"材料 {material.material_name} 的不含税价格为0或不存在，无法进行价格差异分析"
            )
        
        # 计算合同期平均价
        contract_average_price = base_price
        contract_period_prices = []
        
        if contract_info and db:
            related_prices = await self._get_contract_period_prices(db, material, contract_info)
            if related_prices:
                price_values = []
                for related in related_prices:
                    price_value = related.price_excluding_tax or related.price
                    if price_value is None:
                        continue
                    try:
                        price_decimal = Decimal(str(price_value))
                    except Exception:
                        continue

                    related_unit_raw = related.unit or ""
                    related_unit_norm = normalize_unit(related_unit_raw)
                    price_in_project_unit = price_decimal

                    if project_unit and related_unit_norm and related_unit_norm != project_unit:
                        if can_convert_units(related_unit_norm, project_unit):
                            converted_value = convert_unit_price(price_decimal, related_unit_norm, project_unit)
                            if converted_value is None:
                                continue
                            price_in_project_unit = Decimal(str(converted_value)).quantize(
                                Decimal("0.0001"), rounding=ROUND_HALF_UP
                            )
                        else:
                            continue

                    price_values.append(price_in_project_unit)
                if price_values:
                    contract_average_price = (
                        sum(price_values) / Decimal(len(price_values))
                    ).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
                    contract_period_prices = [float(p) for p in price_values]

        # 计算逻辑调整：与前端展示保持一致 (AnalysisDetails.vue)
        
        # 1. 计算风险幅度 (Risk Rate): (合同期平均价 - 基期信息价) / 基期信息价
        risk_rate = Decimal('0')
        if base_price > 0:
            risk_rate = ((contract_average_price - base_price) / base_price).quantize(
                Decimal('0.0001'), rounding=ROUND_HALF_UP
            )
            
        # 2. 计算调差 (Adjustment): 超过 +/- 5% 的部分
        adjustment_unit_price = Decimal('0')
        
        if risk_rate > self.price_threshold:
            adjustment_unit_price = contract_average_price - base_price * (Decimal('1') + self.price_threshold)
        elif risk_rate < -self.price_threshold:
            adjustment_unit_price = contract_average_price - base_price * (Decimal('1') - self.price_threshold)
            
        total_price_difference = adjustment_unit_price * quantity
        
        # 3. 计算价格差异 (Price Diff): 项目单价 - 基期信息价
        price_difference = project_price - base_price
        
        # 变量映射到API响应
        # price_difference_rate 对应 风险幅度
        price_difference_rate = risk_rate
        
        # 判断是否有显著差异 (基于风险幅度是否超过阈值)
        has_difference = abs(risk_rate) > self.price_threshold
        
        # 确定差异等级 (基于风险幅度)
        difference_level = self._get_difference_level(price_difference_rate)
        
        analysis_result = {
            "material_id": material.id,
            "material_name": material.material_name,
            "specification": material.specification or "",
            "unit": project_unit_raw or "",
            "base_unit": base_unit_raw or "",
            "quantity": float(quantity),
            "material_code": material.serial_number or "",
            "remarks": material.notes or "",
            
            # 价格信息
            "project_unit_price": float(project_price),
            "base_unit_price": float(contract_average_price),
            "base_price_including_tax": float(base_price_including_tax),
            "base_price_excluding_tax": float(base_price_excluding_tax),
            "original_base_price": float(base_price),
            "contract_period_prices": contract_period_prices,
            
            # 差异分析
            "unit_price_difference": float(price_difference),
            "total_price_difference": float(total_price_difference),
            "price_difference_rate": float(price_difference_rate),
            "has_difference": has_difference,
            "difference_level": difference_level,
            
            # 基准材料信息
            "base_material_id": material.base_material_id,
            "base_material_name": material.base_material_name,
            "base_specification": material.base_specification or "",
            "base_unit": material.base_unit or "",
            "base_material_code": material.base_material_code or "",
            "category_id": material.category_id,
            "source_type": material.source_type,
            "year_month": material.year_month,
            "region": material.region or "",

            "unit_conversion": {
                "applied": conversion_applied,
                "factor": float(conversion_factor),
                "project_unit": project_unit_raw or "",
                "base_unit": base_unit_raw or "",
                "normalized_project_unit": project_unit,
                "normalized_base_unit": base_unit,
                "original_base_price_excluding_tax": float(original_base_price_excluding_tax),
                "original_base_price_including_tax": float(original_base_price_including_tax),
            },
            
            "analysis_status": "completed",
            "analyzed_at": None  # 将在保存时设置
        }
        
        return analysis_result
    
    def _get_difference_level(self, difference_rate: Decimal) -> str:
        """根据差异率确定差异等级"""
        abs_rate = abs(difference_rate)
        
        if abs_rate < Decimal('0.05'):  # 5%以内
            return "normal"
        elif abs_rate < Decimal('0.15'):  # 5%-15%
            return "low"
        elif abs_rate < Decimal('0.30'):  # 15%-30%
            return "medium"
        else:  # 30%以上
            return "high"
    
    async def _save_analysis_results(self, db: AsyncSession, differences: List[Dict[str, Any]]):
        """保存分析结果到数据库"""
        
        try:
            from app.models.analysis import PriceAnalysis, AnalysisStatus
            from sqlalchemy import delete
            
            for diff in differences:
                # 先删除该材料的旧分析记录（如果存在）
                # 使用 delete 语句直接删除，避免多条记录导致 scalar_one_or_none 报错
                stmt_delete = delete(PriceAnalysis).where(PriceAnalysis.material_id == diff['material_id'])
                await db.execute(stmt_delete)
                
                # 如果分析失败，保存失败状态
                if diff.get('analysis_status') == 'failed':
                    analysis = PriceAnalysis(
                        material_id=diff['material_id'],
                        status=AnalysisStatus.FAILED,
                        analysis_reasoning=f"分析失败: {diff.get('error', '未知错误')}",
                        created_at=func.now(),
                        updated_at=func.now()
                    )
                    db.add(analysis)
                    continue
                
                # 创建新的分析记录
                analysis = PriceAnalysis(
                    material_id=diff['material_id'],
                    status=AnalysisStatus.COMPLETED,
                    
                    # 使用市场信息价作为预测价格
                    predicted_price_min=diff['base_unit_price'],
                    predicted_price_max=diff['base_unit_price'],
                    predicted_price_avg=diff['base_unit_price'],
                    confidence_score=100.0,  # 市场信息价置信度100%
                    
                    # 价格合理性分析
                    is_reasonable=not diff['has_difference'],
                    price_variance=diff['price_difference_rate'] * 100,  # 转换为百分比
                    risk_level=diff['difference_level'],
                    
                    # 分析模型信息
                    analysis_model="guided_price_comparison",
                    
                    # 存储完整的分析结果
                    api_response={
                        "analysis_type": "guided_price",
                        "unit": diff['unit'],
                        "base_unit": diff.get('base_unit'),
                        "project_unit_price": diff['project_unit_price'],
                        "base_unit_price": diff['base_unit_price'],
                        "base_price_including_tax": diff.get('base_price_including_tax'),
                        "base_price_excluding_tax": diff.get('base_price_excluding_tax'),
                        "contract_average_price": diff['base_unit_price'],
                        "contract_period_prices": diff.get('contract_period_prices'),
                        "original_base_price": diff.get('original_base_price'),
                        "unit_price_difference": diff['unit_price_difference'],
                        "total_price_difference": diff['total_price_difference'],
                        "price_difference_rate": diff['price_difference_rate'],
                        "has_difference": diff['has_difference'],
                        "difference_level": diff['difference_level'],
                        "unit_conversion": diff.get('unit_conversion'),
                        "base_material_info": {
                            "id": diff.get('base_material_id'),
                            "name": diff.get('base_material_name'),
                            "specification": diff.get('base_specification'),
                            "source_type": diff.get('source_type'),
                            "region": diff.get('region')
                        }
                    },
                    
                    # 分析说明
                    analysis_reasoning=(
                        f"合同期平均价{diff['base_unit_price']:.2f}元，对比项目单价"
                        f"{diff['project_unit_price']:.2f}元，差异率{diff['price_difference_rate']:.2%}"
                    ),
                    
                    created_at=func.now(),
                    updated_at=func.now()
                )
                
                db.add(analysis)
                
                # 记录日志
                if diff.get('has_difference'):
                    logger.info(
                        f"保存价格差异分析: {diff['material_name']} "
                        f"项目价格: {diff['project_unit_price']}, "
                        f"基准价格: {diff['base_unit_price']}, "
                        f"差异率: {diff['price_difference_rate']:.2%}, "
                        f"合价差: {diff['total_price_difference']:.2f}"
                    )
            
            await db.commit()
            logger.info(f"保存了 {len(differences)} 个材料的市场信息价分析结果到数据库")
            
        except Exception as e:
            logger.error(f"保存分析结果失败: {str(e)}")
            await db.rollback()
            raise
    
    async def _generate_summary(self, differences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成分析摘要"""
        
        total_count = len(differences)
        difference_count = len([d for d in differences if d.get('has_difference')])
        
        # 按差异等级统计
        level_stats = {
            "normal": 0,
            "low": 0,
            "medium": 0,
            "high": 0
        }
        
        total_difference_amount = Decimal('0')
        max_difference_rate = Decimal('0')
        min_difference_rate = Decimal('0')
        
        for diff in differences:
            if diff.get('analysis_status') == 'completed':
                level = diff.get('difference_level', 'normal')
                level_stats[level] += 1
                
                diff_rate = Decimal(str(diff.get('price_difference_rate', 0)))
                total_diff_amount = Decimal(str(diff.get('total_price_difference', 0)))
                
                total_difference_amount += total_diff_amount
                
                if diff_rate > max_difference_rate:
                    max_difference_rate = diff_rate
                if diff_rate < min_difference_rate:
                    min_difference_rate = diff_rate
        
        return {
            "total_analyzed": total_count,
            "total_differences": difference_count,
            "difference_rate": float(difference_count / total_count) if total_count > 0 else 0,
            "level_distribution": level_stats,
            "total_difference_amount": float(total_difference_amount),
            "max_difference_rate": float(max_difference_rate),
            "min_difference_rate": float(min_difference_rate),
            "avg_difference_rate": float(
                sum(Decimal(str(d.get('price_difference_rate', 0))) for d in differences if d.get('analysis_status') == 'completed') / 
                len([d for d in differences if d.get('analysis_status') == 'completed'])
            ) if differences else 0
        }
