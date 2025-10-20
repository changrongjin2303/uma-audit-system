from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.simple_auth import get_current_active_user, require_cost_engineer, SimpleUser
from app.models.user import User
from app.services.matching import MaterialMatchingService
from app.services.project import ProjectService

router = APIRouter()


class HierarchicalMatchingRequest(BaseModel):
    """三级材料匹配请求模型"""
    batch_size: int = 100
    auto_match_threshold: float = 0.85
    # 基期信息价参数
    base_price_date: Optional[str] = None
    base_price_province: Optional[str] = None
    base_price_city: Optional[str] = None
    base_price_district: Optional[str] = None
    # 启用三级地理匹配
    enable_hierarchical_matching: bool = False


@router.post("/{project_id}/match-materials")
async def match_project_materials(
    project_id: int,
    request: HierarchicalMatchingRequest = Body(...),
    # 开发环境暂时移除认证要求
    # current_user: SimpleUser = Depends(require_cost_engineer()),
    db: AsyncSession = Depends(get_db)
):
    """批量匹配项目材料 - 支持三级地理层次匹配"""
    
    # 验证项目存在和权限
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    try:
        matching_service = MaterialMatchingService()

        # 如果启用三级匹配，使用新的三级匹配逻辑
        if request.enable_hierarchical_matching:
            result = await matching_service.hierarchical_match_project_materials(
                db,
                project_id,
                request.batch_size,
                request.auto_match_threshold,
                base_price_date=request.base_price_date,
                base_price_province=request.base_price_province,
                base_price_city=request.base_price_city,
                base_price_district=request.base_price_district
            )
        else:
            # 使用原有的简单匹配逻辑
            result = await matching_service.match_project_materials(
                db, project_id, request.batch_size, request.auto_match_threshold
            )
        
        return {
            "message": "材料匹配完成",
            "project_id": project_id,
            "statistics": result
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"材料匹配失败: {str(e)}"
        )


@router.get("/{project_id}/matching-statistics")
async def get_matching_statistics(
    project_id: int,
    current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取项目材料匹配统计信息"""
    
    # 验证项目存在和权限
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    try:
        matching_service = MaterialMatchingService()
        statistics = await matching_service.get_matching_statistics(db, project_id)
        
        return {
            "project_id": project_id,
            "statistics": statistics
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )


@router.get("/materials/{material_id}/match-candidates")
async def get_material_match_candidates(
    material_id: int,
    top_k: int = 10,
    current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取材料匹配候选项"""
    
    try:
        matching_service = MaterialMatchingService()
        candidates = await matching_service.match_single_material_interactive(
            db, material_id, top_k
        )
        
        return {
            "material_id": material_id,
            "candidates": candidates
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取匹配候选项失败: {str(e)}"
        )


@router.post("/materials/{material_id}/confirm-match")
async def confirm_material_match(
    material_id: int,
    base_material_id: int,
    user_confirmed: bool = True,
    # 开发环境暂时移除认证要求
    # current_user: SimpleUser = Depends(require_cost_engineer()),
    db: AsyncSession = Depends(get_db)
):
    """确认材料匹配"""
    
    try:
        matching_service = MaterialMatchingService()
        success = await matching_service.confirm_material_match(
            db, material_id, base_material_id, user_confirmed
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="确认匹配失败，请检查材料ID是否正确"
            )
        
        return {
            "message": "材料匹配确认成功",
            "material_id": material_id,
            "base_material_id": base_material_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"确认匹配失败: {str(e)}"
        )


@router.delete("/materials/{material_id}/match")
async def unmatch_material(
    material_id: int,
    # 开发环境暂时移除认证要求
    # current_user: SimpleUser = Depends(require_cost_engineer()),
    db: AsyncSession = Depends(get_db)
):
    """取消材料匹配"""
    
    try:
        matching_service = MaterialMatchingService()
        success = await matching_service.unmatch_material(db, material_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="取消匹配失败，材料不存在"
            )
        
        return {
            "message": "材料匹配已取消",
            "material_id": material_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消匹配失败: {str(e)}"
        )