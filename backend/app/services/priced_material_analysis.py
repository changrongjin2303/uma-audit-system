"""
市场信息价材料分析服务

用于分析项目中已匹配材料与市场信息价材料库中价格的差异
"""

from typing import List, Dict, Any
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
        material_ids: List[int],
        batch_size: int = 10
    ) -> Dict[str, Any]:
        """
        分析市场信息价材料价格差异
        
        Args:
            db: 数据库会话
            project_id: 项目ID
            material_ids: 要分析的材料ID列表
            batch_size: 批量处理大小
            
        Returns:
            分析结果字典
        """
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
                analysis = await self._analyze_single_material(material)
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
    
    async def _analyze_single_material(self, material) -> Dict[str, Any]:
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
                base_price = (base_price * factor).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
                base_price_including_tax = (
                    base_price_including_tax * factor
                ).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
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
        
        # 计算价格差异
        price_difference = project_price - base_price
        price_difference_rate = Decimal('0')
        
        if base_price > 0:
            price_difference_rate = (price_difference / base_price).quantize(
                Decimal('0.0001'), rounding=ROUND_HALF_UP
            )
        
        # 计算合价差（单价差 × 数量）
        total_price_difference = price_difference * quantity
        
        # 判断是否有显著差异
        has_difference = abs(price_difference_rate) >= self.price_threshold
        
        # 确定差异等级
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
            "base_unit_price": float(base_price),
            "base_price_including_tax": float(base_price_including_tax),
            "base_price_excluding_tax": float(base_price_excluding_tax),
            
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
            from datetime import datetime
            
            for diff in differences:
                # 先删除该材料的旧分析记录（如果存在）
                stmt_delete = select(PriceAnalysis).where(PriceAnalysis.material_id == diff['material_id'])
                result = await db.execute(stmt_delete)
                existing_analysis = result.scalar_one_or_none()
                if existing_analysis:
                    await db.delete(existing_analysis)
                
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
                    analysis_reasoning=f"市场信息价对比分析：项目单价{diff['project_unit_price']}元，基准价格{diff['base_unit_price']}元，差异率{diff['price_difference_rate']:.2%}",
                    
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
