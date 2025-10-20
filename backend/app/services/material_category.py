"""材料分类管理服务"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, asc
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.models.material import MaterialCategory
from app.models.user import User
from loguru import logger


class MaterialCategoryService:
    """材料分类服务"""
    
    @staticmethod
    async def get_category_tree(
        db: AsyncSession,
        source_type: Optional[str] = None,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """获取分类树结构"""
        try:
            # 构建查询条件
            conditions = [MaterialCategory.level == 1]
            if source_type:
                conditions.append(MaterialCategory.source_type == source_type)
            if not include_inactive:
                conditions.append(MaterialCategory.is_active == True)
            
            # 获取顶级分类
            stmt = select(MaterialCategory).where(and_(*conditions)).order_by(MaterialCategory.sort_order, MaterialCategory.id)
            result = await db.execute(stmt)
            top_categories = result.scalars().all()
            
            category_tree = []
            for category in top_categories:
                category_data = await MaterialCategoryService._build_category_node(db, category, include_inactive)
                category_tree.append(category_data)
            
            return category_tree
            
        except Exception as e:
            logger.error(f"获取分类树失败: {e}")
            return []
    
    @staticmethod
    async def _build_category_node(
        db: AsyncSession, 
        category: MaterialCategory, 
        include_inactive: bool = False
    ) -> Dict[str, Any]:
        """构建分类节点"""
        # 基本信息
        node = {
            "id": category.id,
            "name": category.name,
            "code": category.code,
            "level": category.level,
            "parent_id": category.parent_id,
            "source_type": category.source_type,
            "year_month": category.year_month,
            "sort_order": category.sort_order,
            "is_active": category.is_active,
            "description": category.description,
            "created_at": category.created_at,
            "updated_at": category.updated_at,
            "children": []
        }
        
        # 获取子分类
        conditions = [MaterialCategory.parent_id == category.id]
        if not include_inactive:
            conditions.append(MaterialCategory.is_active == True)
            
        stmt = select(MaterialCategory).where(and_(*conditions)).order_by(MaterialCategory.sort_order, MaterialCategory.id)
        result = await db.execute(stmt)
        children = result.scalars().all()
        
        for child in children:
            child_node = await MaterialCategoryService._build_category_node(db, child, include_inactive)
            node["children"].append(child_node)
        
        return node
    
    @staticmethod
    async def get_categories_by_level(
        db: AsyncSession,
        level: int,
        parent_id: Optional[int] = None,
        source_type: Optional[str] = None
    ) -> List[MaterialCategory]:
        """按层级获取分类"""
        try:
            conditions = [MaterialCategory.level == level, MaterialCategory.is_active == True]
            
            if parent_id is not None:
                conditions.append(MaterialCategory.parent_id == parent_id)
            if source_type:
                conditions.append(MaterialCategory.source_type == source_type)
            
            stmt = select(MaterialCategory).where(and_(*conditions)).order_by(MaterialCategory.sort_order, MaterialCategory.id)
            result = await db.execute(stmt)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"按层级获取分类失败: {e}")
            return []
    
    @staticmethod
    async def create_category(
        db: AsyncSession,
        user: User,
        name: str,
        code: str,
        level: int,
        parent_id: Optional[int] = None,
        source_type: Optional[str] = None,
        year_month: Optional[str] = None,
        description: Optional[str] = None,
        sort_order: int = 0
    ) -> Optional[MaterialCategory]:
        """创建分类"""
        try:
            # 验证父分类（如果有）
            if parent_id:
                parent_stmt = select(MaterialCategory).where(MaterialCategory.id == parent_id)
                parent_result = await db.execute(parent_stmt)
                parent_category = parent_result.scalar_one_or_none()
                if not parent_category:
                    logger.error(f"父分类不存在: {parent_id}")
                    return None
                if parent_category.level != level - 1:
                    logger.error(f"父分类层级错误: {parent_category.level} != {level - 1}")
                    return None
            
            # 检查代码唯一性
            code_stmt = select(MaterialCategory).where(
                and_(
                    MaterialCategory.code == code,
                    MaterialCategory.level == level,
                    MaterialCategory.parent_id == parent_id
                )
            )
            code_result = await db.execute(code_stmt)
            if code_result.scalar_one_or_none():
                logger.error(f"分类代码已存在: {code}")
                return None
            
            # 创建分类
            category = MaterialCategory(
                name=name,
                code=code,
                level=level,
                parent_id=parent_id,
                source_type=source_type,
                year_month=year_month,
                description=description,
                sort_order=sort_order,
                is_active=True
            )
            
            db.add(category)
            await db.commit()
            await db.refresh(category)
            
            logger.info(f"创建分类成功: {name} (ID: {category.id})")
            return category
            
        except Exception as e:
            logger.error(f"创建分类失败: {e}")
            await db.rollback()
            return None
    
    @staticmethod
    async def update_category(
        db: AsyncSession,
        user: User,
        category_id: int,
        **kwargs
    ) -> Optional[MaterialCategory]:
        """更新分类"""
        try:
            stmt = select(MaterialCategory).where(MaterialCategory.id == category_id)
            result = await db.execute(stmt)
            category = result.scalar_one_or_none()
            
            if not category:
                logger.error(f"分类不存在: {category_id}")
                return None
            
            # 更新字段
            for key, value in kwargs.items():
                if hasattr(category, key) and value is not None:
                    setattr(category, key, value)
            
            await db.commit()
            await db.refresh(category)
            
            logger.info(f"更新分类成功: {category.name} (ID: {category_id})")
            return category
            
        except Exception as e:
            logger.error(f"更新分类失败: {e}")
            await db.rollback()
            return None
    
    @staticmethod
    async def delete_category(
        db: AsyncSession,
        user: User,
        category_id: int,
        cascade: bool = False
    ) -> bool:
        """删除分类"""
        try:
            stmt = select(MaterialCategory).where(MaterialCategory.id == category_id)
            result = await db.execute(stmt)
            category = result.scalar_one_or_none()
            
            if not category:
                logger.error(f"分类不存在: {category_id}")
                return False
            
            # 检查是否有子分类
            children_stmt = select(MaterialCategory).where(MaterialCategory.parent_id == category_id)
            children_result = await db.execute(children_stmt)
            children = children_result.scalars().all()
            
            if children and not cascade:
                logger.error(f"分类有子分类，无法删除: {category_id}")
                return False
            
            # 递归删除子分类（如果cascade=True）
            if cascade:
                for child in children:
                    await MaterialCategoryService.delete_category(db, user, child.id, cascade=True)
            
            # 删除分类
            await db.delete(category)
            await db.commit()
            
            logger.info(f"删除分类成功: {category.name} (ID: {category_id})")
            return True
            
        except Exception as e:
            logger.error(f"删除分类失败: {e}")
            await db.rollback()
            return False
    
    @staticmethod
    async def get_year_month_categories(
        db: AsyncSession,
        source_type: str
    ) -> List[MaterialCategory]:
        """获取指定信息来源的年月分类"""
        try:
            # 先获取对应的顶级分类
            parent_stmt = select(MaterialCategory).where(
                and_(
                    MaterialCategory.level == 1,
                    MaterialCategory.source_type == source_type,
                    MaterialCategory.is_active == True
                )
            )
            parent_result = await db.execute(parent_stmt)
            parent_category = parent_result.scalar_one_or_none()
            
            if not parent_category:
                return []
            
            # 获取该分类下的年月分类
            stmt = select(MaterialCategory).where(
                and_(
                    MaterialCategory.level == 2,
                    MaterialCategory.parent_id == parent_category.id,
                    MaterialCategory.is_active == True
                )
            ).order_by(MaterialCategory.year_month.desc())
            
            result = await db.execute(stmt)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"获取年月分类失败: {e}")
            return []
    
    @staticmethod
    async def create_year_month_category(
        db: AsyncSession,
        user: User,
        source_type: str,
        year_month: str,
        description: Optional[str] = None
    ) -> Optional[MaterialCategory]:
        """创建年月分类"""
        try:
            # 获取父分类
            parent_stmt = select(MaterialCategory).where(
                and_(
                    MaterialCategory.level == 1,
                    MaterialCategory.source_type == source_type,
                    MaterialCategory.is_active == True
                )
            )
            parent_result = await db.execute(parent_stmt)
            parent_category = parent_result.scalar_one_or_none()
            
            if not parent_category:
                logger.error(f"找不到信息来源分类: {source_type}")
                return None
            
            # 检查年月分类是否已存在
            existing_stmt = select(MaterialCategory).where(
                and_(
                    MaterialCategory.level == 2,
                    MaterialCategory.parent_id == parent_category.id,
                    MaterialCategory.year_month == year_month
                )
            )
            existing_result = await db.execute(existing_stmt)
            if existing_result.scalar_one_or_none():
                logger.error(f"年月分类已存在: {source_type} - {year_month}")
                return None
            
            # 创建年月分类
            category_name = f"{year_month}期"
            category_code = f"{source_type}_{year_month}"
            
            return await MaterialCategoryService.create_category(
                db=db,
                user=user,
                name=category_name,
                code=category_code,
                level=2,
                parent_id=parent_category.id,
                source_type=source_type,
                year_month=year_month,
                description=description
            )
            
        except Exception as e:
            logger.error(f"创建年月分类失败: {e}")
            return None