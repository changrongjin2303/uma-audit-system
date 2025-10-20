from typing import List, Optional, Dict, Any, Tuple, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text, delete
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
import pandas as pd
from loguru import logger

from app.models.material import BaseMaterial, MaterialAlias
from app.schemas.material import (
    BaseMaterialCreate, BaseMaterialUpdate, BaseMaterialSearchRequest,
    BaseMaterialImportRequest, MaterialAliasCreate
)
from app.utils.excel import ExcelProcessor


class BaseMaterialService:
    """基准材料服务类"""
    
    @staticmethod
    async def create_material(
        db: AsyncSession, 
        material_data: BaseMaterialCreate
    ) -> BaseMaterial:
        """创建基准材料"""
        db_material = BaseMaterial(**material_data.model_dump())
        db.add(db_material)
        await db.commit()
        await db.refresh(db_material)
        return db_material
    
    @staticmethod
    async def get_material_by_id(
        db: AsyncSession, 
        material_id: int
    ) -> Optional[BaseMaterial]:
        """根据ID获取基准材料"""
        stmt = select(BaseMaterial).where(BaseMaterial.id == material_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_materials(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search_params: Optional[BaseMaterialSearchRequest] = None
    ) -> List[BaseMaterial]:
        """获取基准材料列表"""
        stmt = select(BaseMaterial)
        
        # 构建查询条件
        if search_params:
            conditions = []
            
            # 关键词搜索
            if search_params.query:
                search_term = f"%{search_params.query}%"
                conditions.append(
                    or_(
                        BaseMaterial.name.ilike(search_term),
                        BaseMaterial.specification.ilike(search_term),
                        BaseMaterial.material_code.ilike(search_term)
                    )
                )
            
            # 分类过滤
            if search_params.category:
                conditions.append(BaseMaterial.category == search_params.category)
            
            # 新分类系统过滤
            if hasattr(search_params, 'category_id') and search_params.category_id:
                conditions.append(BaseMaterial.category_id == search_params.category_id)
            
            # 地区过滤 - 根据期刊类型使用不同字段
            if search_params.region:
                if hasattr(search_params, 'price_type') and search_params.price_type == 'provincial':
                    # 省刊：使用province字段筛选
                    conditions.append(BaseMaterial.province == search_params.region)
                elif hasattr(search_params, 'price_type') and search_params.price_type == 'municipal':
                    # 市刊：使用region字段筛选
                    conditions.append(BaseMaterial.region == search_params.region)
                else:
                    # 未指定类型：同时匹配province和region字段
                    conditions.append(
                        or_(
                            BaseMaterial.region == search_params.region,
                            BaseMaterial.province == search_params.region
                        )
                    )
            
            # 价格范围过滤
            if search_params.price_min is not None:
                conditions.append(BaseMaterial.price >= search_params.price_min)
            if search_params.price_max is not None:
                conditions.append(BaseMaterial.price <= search_params.price_max)
            
            # 生效日期范围过滤
            if search_params.effective_date_start:
                conditions.append(BaseMaterial.effective_date >= search_params.effective_date_start)
            if search_params.effective_date_end:
                conditions.append(BaseMaterial.effective_date <= search_params.effective_date_end)
            
            # 验证状态过滤
            if search_params.is_verified is not None:
                conditions.append(BaseMaterial.is_verified == search_params.is_verified)
            
            # 信息价类型过滤
            if hasattr(search_params, 'price_type') and search_params.price_type:
                conditions.append(BaseMaterial.price_type == search_params.price_type)
            
            # 信息价期数过滤
            if hasattr(search_params, 'price_date') and search_params.price_date:
                conditions.append(BaseMaterial.price_date == search_params.price_date)
                
            # 信息价来源过滤
            if hasattr(search_params, 'price_source') and search_params.price_source:
                conditions.append(BaseMaterial.price_source.ilike(f"%{search_params.price_source}%"))
            
            if conditions:
                stmt = stmt.where(and_(*conditions))
        
        stmt = stmt.offset(skip).limit(limit).order_by(BaseMaterial.updated_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_materials_count(
        db: AsyncSession,
        search_params: Optional[BaseMaterialSearchRequest] = None
    ) -> int:
        """获取基准材料总数"""
        stmt = select(func.count(BaseMaterial.id))
        
        # 应用相同的搜索条件
        if search_params:
            conditions = []
            
            if search_params.query:
                search_term = f"%{search_params.query}%"
                conditions.append(
                    or_(
                        BaseMaterial.name.ilike(search_term),
                        BaseMaterial.specification.ilike(search_term),
                        BaseMaterial.material_code.ilike(search_term)
                    )
                )
            
            if search_params.category:
                conditions.append(BaseMaterial.category == search_params.category)
            
            # 新分类系统过滤
            if hasattr(search_params, 'category_id') and search_params.category_id:
                conditions.append(BaseMaterial.category_id == search_params.category_id)
            
            # 地区过滤 - 根据期刊类型使用不同字段（与get_materials方法保持一致）
            if search_params.region:
                if hasattr(search_params, 'price_type') and search_params.price_type == 'provincial':
                    # 省刊：使用province字段筛选
                    conditions.append(BaseMaterial.province == search_params.region)
                elif hasattr(search_params, 'price_type') and search_params.price_type == 'municipal':
                    # 市刊：使用region字段筛选
                    conditions.append(BaseMaterial.region == search_params.region)
                else:
                    # 未指定类型：同时匹配province和region字段
                    conditions.append(
                        or_(
                            BaseMaterial.region == search_params.region,
                            BaseMaterial.province == search_params.region
                        )
                    )
            
            if search_params.price_min is not None:
                conditions.append(BaseMaterial.price >= search_params.price_min)
            if search_params.price_max is not None:
                conditions.append(BaseMaterial.price <= search_params.price_max)
            
            if search_params.effective_date_start:
                conditions.append(BaseMaterial.effective_date >= search_params.effective_date_start)
            if search_params.effective_date_end:
                conditions.append(BaseMaterial.effective_date <= search_params.effective_date_end)
            
            if search_params.is_verified is not None:
                conditions.append(BaseMaterial.is_verified == search_params.is_verified)

            # 信息价类型过滤
            if hasattr(search_params, 'price_type') and search_params.price_type:
                conditions.append(BaseMaterial.price_type == search_params.price_type)

            # 信息价期数过滤
            if hasattr(search_params, 'price_date') and search_params.price_date:
                conditions.append(BaseMaterial.price_date == search_params.price_date)

            # 信息价来源过滤
            if hasattr(search_params, 'price_source') and search_params.price_source:
                conditions.append(BaseMaterial.price_source.ilike(f"%{search_params.price_source}%"))

            if conditions:
                stmt = stmt.where(and_(*conditions))
        
        result = await db.execute(stmt)
        return result.scalar() or 0
    
    @staticmethod
    async def update_material(
        db: AsyncSession,
        material: BaseMaterial,
        material_data: BaseMaterialUpdate
    ) -> BaseMaterial:
        """更新基准材料"""
        update_data = material_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(material, field, value)
        
        await db.commit()
        await db.refresh(material)
        return material
    
    @staticmethod
    async def delete_material(
        db: AsyncSession, 
        material: BaseMaterial
    ) -> bool:
        """删除基准材料"""
        try:
            # 检查是否被项目材料引用
            from app.models.project import ProjectMaterial
            stmt = select(ProjectMaterial).where(ProjectMaterial.matched_material_id == material.id)
            result = await db.execute(stmt)
            referenced_materials = result.scalars().all()
            
            if referenced_materials:
                # 如果被项目材料引用，先解除关联（设置为NULL）
                logger.warning(f"基准材料ID {material.id} 被 {len(referenced_materials)} 个项目材料引用，正在解除关联")
                for proj_material in referenced_materials:
                    proj_material.matched_material_id = None
                    proj_material.is_matched = False
                    proj_material.match_score = 0.0
            
            # 先删除相关的材料别名
            from app.models.material import MaterialAlias
            stmt = select(MaterialAlias).where(MaterialAlias.base_material_id == material.id)
            result = await db.execute(stmt)
            aliases = result.scalars().all()
            
            for alias in aliases:
                await db.delete(alias)
            
            # 删除基准材料
            await db.delete(material)
            await db.commit()
            
            logger.info(f"成功删除基准材料 {material.name} (ID: {material.id})")
            return True
        except Exception as e:
            logger.error(f"删除基准材料失败: {e}")
            await db.rollback()
            return False
    
    @staticmethod
    async def batch_verify_materials(
        db: AsyncSession,
        material_ids: List[int],
        is_verified: bool = True,
        verification_notes: Optional[str] = None
    ) -> int:
        """批量验证材料"""
        try:
            stmt = (
                select(BaseMaterial)
                .where(BaseMaterial.id.in_(material_ids))
            )
            result = await db.execute(stmt)
            materials = result.scalars().all()
            
            updated_count = 0
            for material in materials:
                material.is_verified = is_verified
                if verification_notes:
                    material.verification_notes = verification_notes
                updated_count += 1
            
            await db.commit()
            return updated_count
        
        except Exception as e:
            logger.error(f"批量验证材料失败: {e}")
            await db.rollback()
            return 0
    
    @staticmethod
    async def batch_delete_materials(
        db: AsyncSession,
        material_ids: List[int]
    ) -> int:
        """批量删除材料"""
        try:
            # 获取要删除的材料
            stmt = select(BaseMaterial).where(BaseMaterial.id.in_(material_ids))
            result = await db.execute(stmt)
            materials = result.scalars().all()
            
            deleted_count = 0
            
            for material in materials:
                # 检查是否被项目材料引用
                from app.models.project import ProjectMaterial
                stmt_ref = select(ProjectMaterial).where(ProjectMaterial.matched_material_id == material.id)
                ref_result = await db.execute(stmt_ref)
                referenced_materials = ref_result.scalars().all()
                
                if referenced_materials:
                    # 解除项目材料关联
                    logger.warning(f"基准材料ID {material.id} 被 {len(referenced_materials)} 个项目材料引用，正在解除关联")
                    for proj_material in referenced_materials:
                        proj_material.matched_material_id = None
                        proj_material.is_matched = False
                        proj_material.match_score = 0.0
                
                # 删除材料别名
                from app.models.material import MaterialAlias
                stmt_alias = select(MaterialAlias).where(MaterialAlias.base_material_id == material.id)
                alias_result = await db.execute(stmt_alias)
                aliases = alias_result.scalars().all()
                
                for alias in aliases:
                    await db.delete(alias)
                
                # 删除基准材料
                await db.delete(material)
                deleted_count += 1
            
            # 统一提交事务
            await db.commit()
            logger.info(f"成功批量删除 {deleted_count} 个基准材料")
            return deleted_count
        
        except Exception as e:
            logger.error(f"批量删除材料失败: {e}")
            await db.rollback()
            return 0
    
    @staticmethod
    async def get_categories(db: AsyncSession) -> List[str]:
        """获取所有材料分类"""
        stmt = select(BaseMaterial.category).distinct().where(
            BaseMaterial.category.is_not(None)
        )
        result = await db.execute(stmt)
        return [cat for cat in result.scalars().all() if cat]
    
    @staticmethod
    async def get_regions(db: AsyncSession) -> List[str]:
        """获取所有地区"""
        stmt = select(BaseMaterial.region).distinct()
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_regions_by_price_type(db: AsyncSession, price_type: Optional[str] = None) -> List[str]:
        """根据期刊类型获取对应的地区选项"""
        if price_type == "provincial":
            # 省刊：返回所有省份
            stmt = select(BaseMaterial.province).distinct().where(
                and_(
                    BaseMaterial.price_type == "provincial",
                    BaseMaterial.province.is_not(None),
                    BaseMaterial.province != ""
                )
            )
        elif price_type == "municipal":
            # 市刊：返回所有具体地区
            stmt = select(BaseMaterial.region).distinct().where(
                and_(
                    BaseMaterial.price_type == "municipal",
                    BaseMaterial.region.is_not(None),
                    BaseMaterial.region != ""
                )
            )
        else:
            # 没有指定类型：返回所有地区
            stmt = select(BaseMaterial.region).distinct().where(
                and_(
                    BaseMaterial.region.is_not(None),
                    BaseMaterial.region != ""
                )
            )

        result = await db.execute(stmt)
        regions = result.scalars().all()
        return [region for region in regions if region and region.strip()]
    
    @staticmethod
    async def search_similar_materials(
        db: AsyncSession,
        material_name: str,
        specification: Optional[str] = None,
        limit: int = 10
    ) -> List[BaseMaterial]:
        """搜索相似材料"""
        conditions = []
        
        # 使用ILIKE进行模糊匹配
        name_terms = material_name.split()
        for term in name_terms:
            if len(term) > 1:  # 忽略单字符
                conditions.append(BaseMaterial.name.ilike(f"%{term}%"))
        
        if specification:
            spec_terms = specification.split()
            for term in spec_terms:
                if len(term) > 1:
                    conditions.append(BaseMaterial.specification.ilike(f"%{term}%"))
        
        if not conditions:
            return []
        
        stmt = select(BaseMaterial).where(or_(*conditions)).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()


class MaterialImportService:
    """材料导入服务类"""
    
    def __init__(self):
        self.excel_processor = ExcelProcessor()
    
    async def import_materials_from_excel(
        self,
        db: AsyncSession,
        file_path: str,
        import_request: BaseMaterialImportRequest
    ) -> Dict[str, Any]:
        """从Excel文件导入基准材料"""
        try:
            # 读取Excel文件
            df = self.excel_processor.read_excel_file(
                file_path, 
                import_request.sheet_name
            )
            
            # 解析材料数据
            materials_data = self._parse_base_materials(df, import_request.column_mapping)
            
            # 验证数据
            validation_result = await self._validate_materials_data(db, materials_data)
            
            # 批量导入有效数据
            valid_materials = [
                material for material, is_valid in zip(materials_data, validation_result['is_valid'])
                if is_valid
            ]
            
            imported_materials = await self._batch_create_materials(
                db, valid_materials, import_request.batch_size
            )
            
            return {
                'imported_count': len(imported_materials),
                'skipped_count': len(materials_data) - len(valid_materials),
                'error_count': validation_result['error_count'],
                'validation_errors': validation_result['errors'][:10],  # 只返回前10个错误
                'materials': imported_materials[:5]  # 返回前5个样本
            }
        
        except Exception as e:
            logger.error(f"导入基准材料失败: {e}")
            raise ValueError(f"导入失败: {str(e)}")
    
    def _parse_base_materials(
        self, 
        df: pd.DataFrame, 
        column_mapping: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """解析基准材料数据"""
        materials = []
        
        for index, row in df.iterrows():
            try:
                # 获取必需字段
                name = self._safe_get_value(row, column_mapping.get('name'))
                if not name:
                    continue
                
                unit = self._safe_get_value(row, column_mapping.get('unit'))
                if not unit:
                    continue
                
                price = self._safe_get_numeric_value(row, column_mapping.get('price'))
                if price is None or price <= 0:
                    continue
                
                region = self._safe_get_value(row, column_mapping.get('region'))
                if not region:
                    continue
                
                effective_date = self._safe_get_date_value(row, column_mapping.get('effective_date'))
                if not effective_date:
                    continue
                
                material = {
                    'material_code': self._safe_get_value(row, column_mapping.get('material_code')),
                    'name': name,
                    'specification': self._safe_get_value(row, column_mapping.get('specification')),
                    'unit': unit,
                    'category': self._safe_get_value(row, column_mapping.get('category')),
                    'subcategory': self._safe_get_value(row, column_mapping.get('subcategory')),
                    'price': price,
                    'currency': self._safe_get_value(row, column_mapping.get('currency', 'CNY')),
                    'region': region,
                    'province': self._safe_get_value(row, column_mapping.get('province')),
                    'city': self._safe_get_value(row, column_mapping.get('city')),
                    'version': self._safe_get_value(row, column_mapping.get('version')),
                    'effective_date': effective_date,
                    'source': self._safe_get_value(row, column_mapping.get('source')),
                    'source_url': self._safe_get_value(row, column_mapping.get('source_url')),
                    'row_number': index + 1
                }
                
                materials.append(material)
            
            except Exception as e:
                logger.warning(f"解析第{index + 1}行数据时出错: {e}")
                continue
        
        return materials
    
    def _safe_get_value(self, row: pd.Series, column_name: Optional[str]) -> Optional[str]:
        """安全获取字符串值"""
        if not column_name or column_name not in row:
            return None
        
        value = row[column_name]
        if pd.isna(value):
            return None
        
        return str(value).strip() if str(value).strip() else None
    
    def _safe_get_numeric_value(self, row: pd.Series, column_name: Optional[str]) -> Optional[float]:
        """安全获取数值"""
        if not column_name or column_name not in row:
            return None
        
        value = row[column_name]
        if pd.isna(value):
            return None
        
        try:
            if isinstance(value, (int, float)):
                return float(value)
            
            str_value = str(value).strip().replace(',', '').replace('¥', '').replace('￥', '')
            if str_value:
                return float(str_value)
        except (ValueError, TypeError):
            pass
        
        return None
    
    def _safe_get_date_value(self, row: pd.Series, column_name: Optional[str]) -> Optional[datetime]:
        """安全获取日期值"""
        if not column_name or column_name not in row:
            return datetime.now()  # 默认当前时间
        
        value = row[column_name]
        if pd.isna(value):
            return datetime.now()
        
        try:
            if isinstance(value, datetime):
                return value
            elif isinstance(value, pd.Timestamp):
                return value.to_pydatetime()
            else:
                # 尝试解析字符串日期
                return pd.to_datetime(str(value)).to_pydatetime()
        except Exception:
            return datetime.now()
    
    async def _validate_materials_data(
        self, 
        db: AsyncSession, 
        materials_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """验证材料数据"""
        validation_result = {
            'is_valid': [],
            'errors': [],
            'error_count': 0
        }
        
        for material in materials_data:
            is_valid = True
            errors = []
            
            # 检查重复数据（基于材料编码+名称+规格+备注+地区）
            existing_stmt = select(BaseMaterial).where(
                and_(
                    BaseMaterial.material_code == material.get('material_code', ''),
                    BaseMaterial.name == material['name'],
                    BaseMaterial.specification == material.get('specification', ''),
                    BaseMaterial.verification_notes == material.get('verification_notes', ''),
                    BaseMaterial.region == material.get('region', '')
                )
            )
            result = await db.execute(existing_stmt)
            existing_material = result.scalars().first()

            if existing_material:
                is_valid = False
                material_code = material.get('material_code', '无编码')
                errors.append(f"第{material['row_number']}行: 材料已存在 (编码:{material_code})")
            
            validation_result['is_valid'].append(is_valid)
            if not is_valid:
                validation_result['error_count'] += 1
                validation_result['errors'].extend(errors)
        
        return validation_result
    
    async def _batch_create_materials(
        self,
        db: AsyncSession,
        materials_data: List[Dict[str, Any]],
        batch_size: int = 1000
    ) -> List[BaseMaterial]:
        """批量创建材料"""
        created_materials = []
        
        for i in range(0, len(materials_data), batch_size):
            batch = materials_data[i:i + batch_size]
            
            db_materials = []
            for material_data in batch:
                material_data.pop('row_number', None)  # 移除不需要的字段
                db_material = BaseMaterial(**material_data)
                db_materials.append(db_material)
            
            db.add_all(db_materials)
            await db.commit()
            
            for material in db_materials:
                await db.refresh(material)
            
            created_materials.extend(db_materials)
        
        return created_materials
    
    async def import_base_materials(
        self, 
        db: AsyncSession,
        materials_data: List[Dict[str, Any]],
        field_mapping: Dict[str, str],
        import_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """从解析后的数据导入基础材料"""
        try:
            # 转换和验证材料数据
            processed_materials = []
            errors = []
            
            for idx, material_row in enumerate(materials_data):
                try:
                    # 根据字段映射提取数据
                    material_data = {}
                    
                    # 必填字段映射
                    if field_mapping.get('name'):
                        material_data['name'] = str(material_row.get(field_mapping['name'], '')).strip()
                    if field_mapping.get('unit'):
                        material_data['unit'] = str(material_row.get(field_mapping['unit'], '')).strip()
                    if field_mapping.get('price'):
                        price_str = str(material_row.get(field_mapping['price'], 0))
                        try:
                            material_data['price'] = float(price_str.replace(',', '').replace('¥', '').replace('￥', '')) if price_str else 0.0
                        except (ValueError, TypeError):
                            material_data['price'] = 0.0
                    
                    # 可选字段映射
                    if field_mapping.get('specification'):
                        material_data['specification'] = str(material_row.get(field_mapping['specification'], '')).strip()
                    if field_mapping.get('category'):
                        material_data['category'] = str(material_row.get(field_mapping['category'], '')).strip()
                    if field_mapping.get('region'):
                        material_data['region'] = str(material_row.get(field_mapping['region'], '')).strip()
                    if field_mapping.get('source'):
                        material_data['source'] = str(material_row.get(field_mapping['source'], '')).strip()
                    
                    # 数据验证
                    if not material_data.get('name'):
                        errors.append(f"第{idx+1}行: 材料名称不能为空")
                        continue
                    if not material_data.get('unit'):
                        errors.append(f"第{idx+1}行: 单位不能为空")
                        continue
                    if not material_data.get('price') or material_data['price'] <= 0:
                        errors.append(f"第{idx+1}行: 单价必须大于0")
                        continue
                    
                    # 设置默认值和必填字段
                    material_data.setdefault('specification', '')
                    material_data.setdefault('category', '其他')
                    material_data.setdefault('region', '全国')
                    material_data.setdefault('source', '导入数据')
                    material_data.setdefault('is_verified', True)
                    
                    # 设置必填的日期字段
                    from datetime import datetime
                    material_data.setdefault('effective_date', datetime.now())
                    
                    processed_materials.append(material_data)
                    
                except Exception as e:
                    errors.append(f"第{idx+1}行: 数据处理错误 - {str(e)}")
            
            # 检查重复材料（根据选项）- 使用高性能批量检查（基于材料编码+名称+规格+备注+地区）
            if import_options.get('skip_duplicate', True):
                unique_materials = []
                
                # 批量检查重复材料，基于材料编码+名称+规格+备注+地区
                existing_materials = await self._batch_check_materials_exist(
                    db, processed_materials
                )
                
                for material in processed_materials:
                    # 使用材料编码+材料名称+规格型号+备注+地区作为重复判断依据
                    material_key = f"{material.get('material_code', '')}|{material['name']}|{material.get('specification', '')}|{material.get('verification_notes', '')}|{material.get('region', '')}"
                    if material_key not in existing_materials:
                        unique_materials.append(material)
                    else:
                        code_info = material.get('material_code', '无编码')
                        errors.append(f"材料 '{material['name']}' (编码:{code_info}) 已存在，跳过")
                
                processed_materials = unique_materials
            
            # 批量创建材料
            created_materials = []
            if processed_materials:
                try:
                    # 分批处理，根据数据量动态调整批量大小
                    total_count = len(processed_materials)
                    if total_count <= 1000:
                        batch_size = 500  # 小数据量：每批500条
                    elif total_count <= 5000:
                        batch_size = 1000  # 中等数据量：每批1000条
                    else:
                        batch_size = 2000  # 大数据量：每批2000条
                    
                    logger.info(f"开始批量导入 {total_count} 条材料数据，批量大小：{batch_size}")
                    for i in range(0, len(processed_materials), batch_size):
                        batch = processed_materials[i:i + batch_size]
                        current_batch = i // batch_size + 1
                        total_batches = (len(processed_materials) + batch_size - 1) // batch_size
                        
                        logger.info(f"处理第 {current_batch}/{total_batches} 批，数量: {len(batch)}")
                        
                        db_materials = []
                        
                        for material_data in batch:
                            db_material = BaseMaterial(**material_data)
                            db_materials.append(db_material)
                        
                        db.add_all(db_materials)
                        await db.commit()
                        
                        for material in db_materials:
                            await db.refresh(material)
                        
                        created_materials.extend(db_materials)
                        
                        logger.info(f"第 {current_batch} 批处理完成，已成功导入: {len(created_materials)}/{total_count}")
                        
                except Exception as e:
                    logger.error(f"批量创建材料失败: {e}")
                    errors.append(f"批量创建失败: {str(e)}")
            
            return {
                "total_count": len(materials_data),
                "success_count": len(created_materials),
                "failed_count": len(materials_data) - len(created_materials),
                "skipped_count": len(materials_data) - len(processed_materials) - len(created_materials),
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"导入基础材料失败: {e}")
            raise ValueError(f"导入失败: {str(e)}")
    
    async def import_structured_materials(
        self, 
        db: AsyncSession,
        structured_materials: List[Dict[str, Any]],
        import_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """导入已经结构化处理的材料数据"""
        try:
            processed_materials = []
            errors = []
            
            for idx, material_data in enumerate(structured_materials):
                try:
                    # 数据验证
                    if not material_data.get('name'):
                        errors.append(f"第{idx+1}行: 材料名称不能为空")
                        continue
                    if not material_data.get('unit'):
                        errors.append(f"第{idx+1}行: 单位不能为空")
                        continue
                    
                    # 检查价格字段 - 支持新的双价格字段
                    price_excluding_tax = material_data.get('price_excluding_tax')
                    price_including_tax = material_data.get('price_including_tax')
                    old_price = material_data.get('price')  # 兼容旧字段
                    
                    if price_excluding_tax and float(price_excluding_tax) > 0:
                        main_price = float(price_excluding_tax)
                    elif old_price and float(old_price) > 0:
                        main_price = float(old_price)
                    else:
                        errors.append(f"第{idx+1}行: 价格必须大于0")
                        continue
                    
                    # 设置默认值，包含BaseMaterial模型支持的所有字段
                    processed_data = {
                        'material_code': str(material_data.get('material_code', '')).strip(),
                        'name': str(material_data['name']).strip(),
                        'specification': str(material_data.get('specification', '')).strip(),
                        'unit': str(material_data['unit']).strip(),
                        'category': str(material_data.get('category', '其他')).strip(),
                        'price': main_price,  # 使用验证过的主价格
                        'price_excluding_tax': float(price_excluding_tax) if price_excluding_tax else None,
                        'price_including_tax': float(price_including_tax) if price_including_tax else None,
                        'currency': str(material_data.get('currency', 'CNY')).strip(),
                        'region': str(material_data.get('region', '全国')).strip(),
                        'province': str(material_data.get('province', '')).strip(),
                        'city': str(material_data.get('city', '')).strip(),
                        'version': str(material_data.get('version', '')).strip(),
                        'source': str(material_data.get('source', '导入数据')).strip(),
                        'source_url': str(material_data.get('source_url', '')).strip(),
                        'price_type': str(material_data.get('price_type', '')).strip(),
                        'price_date': str(material_data.get('price_date', '')).strip(),
                        'price_source': str(material_data.get('price_source', '')).strip(),
                        'is_verified': material_data.get('is_verified', True),
                        'verification_notes': str(material_data.get('remarks', material_data.get('verification_notes', ''))).strip(),
                    }
                    
                    # 设置必填的日期字段
                    from datetime import datetime
                    processed_data['effective_date'] = datetime.now()
                    
                    processed_materials.append(processed_data)
                    
                except Exception as e:
                    errors.append(f"第{idx+1}行: 数据处理错误 - {str(e)}")
            
            # 检查重复材料（根据选项）- 使用高性能批量检查（基于材料编码+名称+规格+备注+地区）
            if import_options.get('skip_duplicate', True):
                unique_materials = []
                
                # 批量检查重复材料，基于材料编码+名称+规格+备注+地区
                existing_materials = await self._batch_check_materials_exist(
                    db, processed_materials
                )
                
                for material in processed_materials:
                    # 使用材料编码+材料名称+规格型号+备注+地区作为重复判断依据
                    material_key = f"{material.get('material_code', '')}|{material['name']}|{material.get('specification', '')}|{material.get('verification_notes', '')}|{material.get('region', '')}"
                    if material_key not in existing_materials:
                        unique_materials.append(material)
                    else:
                        code_info = material.get('material_code', '无编码')
                        errors.append(f"材料 '{material['name']}' (编码:{code_info}) 已存在，跳过")
                
                processed_materials = unique_materials
            
            # 批量创建材料
            created_materials = []
            if processed_materials:
                try:
                    # 分批处理，根据数据量动态调整批量大小
                    total_count = len(processed_materials)
                    if total_count <= 1000:
                        batch_size = 500  # 小数据量：每批500条
                    elif total_count <= 5000:
                        batch_size = 1000  # 中等数据量：每批1000条
                    else:
                        batch_size = 2000  # 大数据量：每批2000条
                    
                    logger.info(f"开始批量导入 {total_count} 条材料数据，批量大小：{batch_size}")
                    for i in range(0, len(processed_materials), batch_size):
                        batch = processed_materials[i:i + batch_size]
                        current_batch = i // batch_size + 1
                        total_batches = (len(processed_materials) + batch_size - 1) // batch_size
                        
                        logger.info(f"处理第 {current_batch}/{total_batches} 批，数量: {len(batch)}")
                        
                        db_materials = []
                        
                        for material_data in batch:
                            db_material = BaseMaterial(**material_data)
                            db_materials.append(db_material)
                        
                        db.add_all(db_materials)
                        await db.commit()
                        
                        for material in db_materials:
                            await db.refresh(material)
                        
                        created_materials.extend(db_materials)
                        
                        logger.info(f"第 {current_batch} 批处理完成，已成功导入: {len(created_materials)}/{total_count}")
                        
                except Exception as e:
                    logger.error(f"批量创建材料失败: {e}")
                    errors.append(f"批量创建失败: {str(e)}")
            
            return {
                "total_count": len(structured_materials),
                "success_count": len(created_materials),
                "failed_count": len(structured_materials) - len(created_materials),
                "skipped_count": len(structured_materials) - len(processed_materials) - len(created_materials),
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"导入结构化材料失败: {e}")
            raise ValueError(f"导入失败: {str(e)}")
    
    async def _check_material_exists(
        self, 
        db: AsyncSession, 
        name: str, 
        specification: str = "",
        region: str = ""
    ) -> bool:
        """检查材料是否已存在（考虑地区）"""
        stmt = select(BaseMaterial).where(
            and_(
                BaseMaterial.name == name,
                BaseMaterial.specification == specification,
                BaseMaterial.region == region
            )
        )
        result = await db.execute(stmt)
        return result.scalars().first() is not None
    
    async def _batch_check_materials_exist(
        self, 
        db: AsyncSession, 
        materials: List[Dict[str, Any]]
    ) -> Set[str]:
        """批量检查材料是否已存在，返回存在的材料键集合（基于材料编码+名称+规格+备注+地区）"""
        if not materials:
            return set()
        
        # 构建查询条件
        conditions = []
        material_keys = set()
        
        for material in materials:
            material_code = material.get('material_code', '')
            name = material['name']
            specification = material.get('specification', '')
            verification_notes = material.get('verification_notes', '')
            region = material.get('region', '')
            material_key = f"{material_code}|{name}|{specification}|{verification_notes}|{region}"
            material_keys.add(material_key)

            conditions.append(
                and_(
                    BaseMaterial.material_code == material_code,
                    BaseMaterial.name == name,
                    BaseMaterial.specification == specification,
                    BaseMaterial.verification_notes == verification_notes,
                    BaseMaterial.region == region
                )
            )
        
        # 分批查询，避免SQL语句过长
        existing_materials = set()
        batch_size = 1000  # 每次查询最多1000个条件
        
        for i in range(0, len(conditions), batch_size):
            batch_conditions = conditions[i:i + batch_size]
            stmt = select(BaseMaterial.material_code, BaseMaterial.name, BaseMaterial.specification, BaseMaterial.verification_notes, BaseMaterial.region).where(
                or_(*batch_conditions)
            )

            result = await db.execute(stmt)
            for row in result:
                existing_key = f"{row.material_code or ''}|{row.name}|{row.specification or ''}|{row.verification_notes or ''}|{row.region or ''}"
                existing_materials.add(existing_key)
        
        return existing_materials