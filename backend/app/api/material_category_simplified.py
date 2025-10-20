"""材料分类管理API - 简化版"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.material_category import MaterialCategoryService

router = APIRouter(prefix="/material-categories", tags=["material-categories"])


@router.get("/tree")
async def get_category_tree(
    source_type: Optional[str] = Query(None, description="信息来源类型 (municipal/provincial)"),
    include_inactive: bool = Query(False, description="是否包含未启用的分类"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取分类树结构"""
    try:
        tree = await MaterialCategoryService.get_category_tree(
            db=db,
            source_type=source_type,
            include_inactive=include_inactive
        )
        return {"code": 200, "message": "获取成功", "data": tree}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类树失败: {str(e)}")


@router.get("/level/{level}")
async def get_categories_by_level(
    level: int,
    parent_id: Optional[int] = Query(None, description="父分类ID"),
    source_type: Optional[str] = Query(None, description="信息来源类型"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """按层级获取分类"""
    try:
        categories = await MaterialCategoryService.get_categories_by_level(
            db=db,
            level=level,
            parent_id=parent_id,
            source_type=source_type
        )
        
        categories_data = []
        for category in categories:
            categories_data.append({
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
                "updated_at": category.updated_at
            })
        
        return {"code": 200, "message": "获取成功", "data": categories_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类失败: {str(e)}")


@router.get("/source-types")
async def get_source_types(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有信息来源类型"""
    try:
        source_types = [
            {
                "value": "municipal",
                "label": "市造价信息正刊",
                "description": "市级造价信息发布机构发布的正式刊物"
            },
            {
                "value": "provincial",
                "label": "省造价信息正刊",
                "description": "省级造价信息发布机构发布的正式刊物"
            }
        ]
        return {"code": 200, "message": "获取成功", "data": source_types}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取信息来源类型失败: {str(e)}")


@router.get("/year-month/{source_type}")
async def get_year_month_categories(
    source_type: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取指定信息来源的年月分类"""
    try:
        categories = await MaterialCategoryService.get_year_month_categories(
            db=db,
            source_type=source_type
        )
        
        categories_data = []
        for category in categories:
            categories_data.append({
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
                "updated_at": category.updated_at
            })
        
        return {"code": 200, "message": "获取成功", "data": categories_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取年月分类失败: {str(e)}")