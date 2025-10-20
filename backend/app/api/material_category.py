"""材料分类管理API"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.material_category import MaterialCategoryService
# 响应格式将直接返回数据

router = APIRouter(prefix="/api/v1/material-categories", tags=["material-categories"])


class CategoryCreateRequest(BaseModel):
    """分类创建请求"""
    name: str
    code: str
    level: int
    parent_id: Optional[int] = None
    source_type: Optional[str] = None
    year_month: Optional[str] = None
    description: Optional[str] = None
    sort_order: int = 0


class CategoryUpdateRequest(BaseModel):
    """分类更新请求"""
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class YearMonthCategoryRequest(BaseModel):
    """年月分类创建请求"""
    source_type: str
    year_month: str
    description: Optional[str] = None


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


@router.post("/")
async def create_category(
    request: CategoryCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建分类"""
    try:
        category = await MaterialCategoryService.create_category(
            db=db,
            user=current_user,
            name=request.name,
            code=request.code,
            level=request.level,
            parent_id=request.parent_id,
            source_type=request.source_type,
            year_month=request.year_month,
            description=request.description,
            sort_order=request.sort_order
        )
        
        if not category:
            raise HTTPException(status_code=400, detail="创建分类失败")
        
        category_data = {
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
        }
        
        return {"code": 200, "message": "创建分类成功", "data": category_data}
        
    except Exception as e:
        return error_response(f"创建分类失败: {str(e)}")


@router.put("/{category_id}")
async def update_category(
    category_id: int,
    request: CategoryUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新分类"""
    try:
        update_data = request.dict(exclude_unset=True)
        
        category = await MaterialCategoryService.update_category(
            db=db,
            user=current_user,
            category_id=category_id,
            **update_data
        )
        
        if not category:
            return error_response("分类不存在或更新失败")
        
        category_data = {
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
        }
        
        return success_response(data=category_data, message="更新分类成功")
        
    except Exception as e:
        return error_response(f"更新分类失败: {str(e)}")


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    cascade: bool = Query(False, description="是否级联删除子分类"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除分类"""
    try:
        success = await MaterialCategoryService.delete_category(
            db=db,
            user=current_user,
            category_id=category_id,
            cascade=cascade
        )
        
        if not success:
            return error_response("分类不存在或删除失败")
        
        return success_response(message="删除分类成功")
        
    except Exception as e:
        return error_response(f"删除分类失败: {str(e)}")


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
        return error_response(f"获取年月分类失败: {str(e)}")


@router.post("/year-month")
async def create_year_month_category(
    request: YearMonthCategoryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建年月分类"""
    try:
        category = await MaterialCategoryService.create_year_month_category(
            db=db,
            user=current_user,
            source_type=request.source_type,
            year_month=request.year_month,
            description=request.description
        )
        
        if not category:
            return error_response("创建年月分类失败")
        
        category_data = {
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
        }
        
        return success_response(data=category_data, message="创建年月分类成功")
        
    except Exception as e:
        return error_response(f"创建年月分类失败: {str(e)}")


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
        
        return success_response(data=source_types)
        
    except Exception as e:
        return error_response(f"获取信息来源类型失败: {str(e)}")