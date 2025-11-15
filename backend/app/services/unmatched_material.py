from typing import List, Optional, Dict, Any, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from datetime import datetime
import pandas as pd
from loguru import logger

from app.models.unmatched_material import UnmatchedMaterial
from app.schemas.unmatched_material import (
    UnmatchedMaterialCreate, UnmatchedMaterialUpdate, UnmatchedMaterialSearchRequest,
    UnmatchedMaterialImportRequest
)
from app.utils.excel import ExcelProcessor


class UnmatchedMaterialService:
    """无市场信息价材料服务类"""

    @staticmethod
    async def create_material(
        db: AsyncSession,
        material_data: UnmatchedMaterialCreate
    ) -> UnmatchedMaterial:
        """创建无市场信息价材料"""
        db_material = UnmatchedMaterial(**material_data.model_dump())
        db.add(db_material)
        await db.commit()
        await db.refresh(db_material)
        return db_material

    @staticmethod
    async def get_material_by_id(
        db: AsyncSession,
        material_id: int
    ) -> Optional[UnmatchedMaterial]:
        """根据ID获取无市场信息价材料"""
        stmt = select(UnmatchedMaterial).where(UnmatchedMaterial.id == material_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_materials(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search_params: Optional[UnmatchedMaterialSearchRequest] = None
    ) -> List[UnmatchedMaterial]:
        """获取无市场信息价材料列表"""
        stmt = select(UnmatchedMaterial)

        # 构建查询条件
        if search_params:
            conditions = []

            # 关键词搜索
            if search_params.query:
                search_term = f"%{search_params.query}%"
                conditions.append(
                    or_(
                        UnmatchedMaterial.name.ilike(search_term),
                        UnmatchedMaterial.specification.ilike(search_term),
                        UnmatchedMaterial.serial_number.ilike(search_term)
                    )
                )

            # 分类过滤
            if search_params.category:
                conditions.append(UnmatchedMaterial.category == search_params.category)

            # 价格范围过滤
            if search_params.price_min is not None:
                conditions.append(UnmatchedMaterial.price_excluding_tax >= search_params.price_min)
            if search_params.price_max is not None:
                conditions.append(UnmatchedMaterial.price_excluding_tax <= search_params.price_max)

            # 日期范围过滤
            if search_params.date_start:
                conditions.append(UnmatchedMaterial.date >= search_params.date_start)
            if search_params.date_end:
                conditions.append(UnmatchedMaterial.date <= search_params.date_end)

            # 验证状态过滤
            if search_params.is_verified is not None:
                conditions.append(UnmatchedMaterial.is_verified == search_params.is_verified)

            if conditions:
                stmt = stmt.where(and_(*conditions))

        stmt = stmt.offset(skip).limit(limit).order_by(UnmatchedMaterial.updated_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_materials_count(
        db: AsyncSession,
        search_params: Optional[UnmatchedMaterialSearchRequest] = None
    ) -> int:
        """获取无市场信息价材料总数"""
        stmt = select(func.count(UnmatchedMaterial.id))

        # 应用相同的搜索条件
        if search_params:
            conditions = []

            if search_params.query:
                search_term = f"%{search_params.query}%"
                conditions.append(
                    or_(
                        UnmatchedMaterial.name.ilike(search_term),
                        UnmatchedMaterial.specification.ilike(search_term),
                        UnmatchedMaterial.serial_number.ilike(search_term)
                    )
                )

            if search_params.category:
                conditions.append(UnmatchedMaterial.category == search_params.category)

            if search_params.price_min is not None:
                conditions.append(UnmatchedMaterial.price_excluding_tax >= search_params.price_min)
            if search_params.price_max is not None:
                conditions.append(UnmatchedMaterial.price_excluding_tax <= search_params.price_max)

            if search_params.date_start:
                conditions.append(UnmatchedMaterial.date >= search_params.date_start)
            if search_params.date_end:
                conditions.append(UnmatchedMaterial.date <= search_params.date_end)

            if search_params.is_verified is not None:
                conditions.append(UnmatchedMaterial.is_verified == search_params.is_verified)

            if conditions:
                stmt = stmt.where(and_(*conditions))

        result = await db.execute(stmt)
        return result.scalar() or 0

    @staticmethod
    async def update_material(
        db: AsyncSession,
        material: UnmatchedMaterial,
        material_data: UnmatchedMaterialUpdate
    ) -> UnmatchedMaterial:
        """更新无市场信息价材料"""
        update_data = material_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(material, field, value)

        await db.commit()
        await db.refresh(material)
        return material

    @staticmethod
    async def delete_material(
        db: AsyncSession,
        material: UnmatchedMaterial
    ) -> bool:
        """删除无市场信息价材料"""
        try:
            await db.delete(material)
            await db.commit()
            logger.info(f"成功删除无市场信息价材料 {material.name} (ID: {material.id})")
            return True
        except Exception as e:
            logger.error(f"删除无市场信息价材料失败: {e}")
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
                select(UnmatchedMaterial)
                .where(UnmatchedMaterial.id.in_(material_ids))
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
            stmt = select(UnmatchedMaterial).where(UnmatchedMaterial.id.in_(material_ids))
            result = await db.execute(stmt)
            materials = result.scalars().all()

            deleted_count = 0

            for material in materials:
                await db.delete(material)
                deleted_count += 1

            await db.commit()
            logger.info(f"成功批量删除 {deleted_count} 个无市场信息价材料")
            return deleted_count

        except Exception as e:
            logger.error(f"批量删除材料失败: {e}")
            await db.rollback()
            return 0

    @staticmethod
    async def get_categories(db: AsyncSession) -> List[str]:
        """获取所有材料分类"""
        stmt = select(UnmatchedMaterial.category).distinct().where(
            UnmatchedMaterial.category.is_not(None)
        )
        result = await db.execute(stmt)
        return [cat for cat in result.scalars().all() if cat]

    @staticmethod
    async def search_similar_materials(
        db: AsyncSession,
        material_name: str,
        specification: Optional[str] = None,
        limit: int = 10
    ) -> List[UnmatchedMaterial]:
        """搜索相似材料"""
        conditions = []

        # 使用ILIKE进行模糊匹配
        name_terms = material_name.split()
        for term in name_terms:
            if len(term) > 1:  # 忽略单字符
                conditions.append(UnmatchedMaterial.name.ilike(f"%{term}%"))

        if specification:
            spec_terms = specification.split()
            for term in spec_terms:
                if len(term) > 1:
                    conditions.append(UnmatchedMaterial.specification.ilike(f"%{term}%"))

        if not conditions:
            return []

        stmt = select(UnmatchedMaterial).where(or_(*conditions)).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()


class UnmatchedMaterialImportService:
    """无市场信息价材料导入服务类"""

    def __init__(self):
        self.excel_processor = ExcelProcessor()

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
                    # 数据验证 - 只验证名称必填
                    if not material_data.get('name'):
                        errors.append(f"第{idx+1}行: 材料名称不能为空")
                        continue

                    # 设置默认值
                    processed_data = {
                        'serial_number': str(material_data.get('serial_number', '')).strip(),
                        'name': str(material_data['name']).strip(),
                        'specification': str(material_data.get('specification', '')).strip(),
                        'brand': str(material_data.get('brand', '')).strip(),
                        'unit': str(material_data.get('unit', '')).strip() if material_data.get('unit') else None,
                        'category': str(material_data.get('category', '其他')).strip(),
                        'subcategory': str(material_data.get('subcategory', '')).strip(),
                        'price_excluding_tax': float(material_data['price_excluding_tax']) if material_data.get('price_excluding_tax') else None,
                        'currency': str(material_data.get('currency', 'CNY')).strip(),
                        'source': str(material_data.get('source', '导入数据')).strip(),
                        'source_url': str(material_data.get('source_url', '')).strip(),
                        'notes': str(material_data.get('notes', material_data.get('remarks', ''))).strip(),
                        'is_verified': material_data.get('is_verified', False),
                        'verification_notes': str(material_data.get('verification_notes', '')).strip(),
                    }

                    # 处理日期字段
                    if material_data.get('date'):
                        try:
                            if isinstance(material_data['date'], datetime):
                                processed_data['date'] = material_data['date']
                            else:
                                processed_data['date'] = pd.to_datetime(str(material_data['date'])).to_pydatetime()
                        except:
                            processed_data['date'] = None

                    processed_materials.append(processed_data)

                except Exception as e:
                    errors.append(f"第{idx+1}行: 数据处理错误 - {str(e)}")

            # 检查重复材料（基于序号+名称+规格）
            if import_options.get('skip_duplicate', True):
                unique_materials = []

                existing_materials = await self._batch_check_materials_exist(
                    db, processed_materials
                )

                for material in processed_materials:
                    material_key = f"{material.get('serial_number', '')}|{material['name']}|{material.get('specification', '')}"
                    if material_key not in existing_materials:
                        unique_materials.append(material)
                    else:
                        serial_info = material.get('serial_number', '无序号')
                        errors.append(f"材料 '{material['name']}' (序号:{serial_info}) 已存在，跳过")

                processed_materials = unique_materials

            # 批量创建材料
            created_materials = []
            if processed_materials:
                try:
                    # 分批处理
                    total_count = len(processed_materials)
                    if total_count <= 1000:
                        batch_size = 500
                    elif total_count <= 5000:
                        batch_size = 1000
                    else:
                        batch_size = 2000

                    logger.info(f"开始批量导入 {total_count} 条无市场信息价材料数据，批量大小：{batch_size}")
                    for i in range(0, len(processed_materials), batch_size):
                        batch = processed_materials[i:i + batch_size]
                        current_batch = i // batch_size + 1
                        total_batches = (len(processed_materials) + batch_size - 1) // batch_size

                        logger.info(f"处理第 {current_batch}/{total_batches} 批，数量: {len(batch)}")

                        db_materials = []

                        for material_data in batch:
                            db_material = UnmatchedMaterial(**material_data)
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

    async def _batch_check_materials_exist(
        self,
        db: AsyncSession,
        materials: List[Dict[str, Any]]
    ) -> Set[str]:
        """批量检查材料是否已存在，返回存在的材料键集合（基于序号+名称+规格）"""
        if not materials:
            return set()

        # 构建查询条件
        conditions = []
        material_keys = set()

        for material in materials:
            serial_number = material.get('serial_number', '')
            name = material['name']
            specification = material.get('specification', '')
            material_key = f"{serial_number}|{name}|{specification}"
            material_keys.add(material_key)

            conditions.append(
                and_(
                    UnmatchedMaterial.serial_number == serial_number,
                    UnmatchedMaterial.name == name,
                    UnmatchedMaterial.specification == specification
                )
            )

        # 分批查询，避免SQL语句过长
        existing_materials = set()
        batch_size = 1000

        for i in range(0, len(conditions), batch_size):
            batch_conditions = conditions[i:i + batch_size]
            stmt = select(UnmatchedMaterial.serial_number, UnmatchedMaterial.name, UnmatchedMaterial.specification).where(
                or_(*batch_conditions)
            )

            result = await db.execute(stmt)
            for row in result:
                existing_key = f"{row.serial_number or ''}|{row.name}|{row.specification or ''}"
                existing_materials.add(existing_key)

        return existing_materials
