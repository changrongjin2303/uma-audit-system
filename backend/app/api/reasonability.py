from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.simple_auth import get_current_active_user, require_cost_engineer, SimpleUser
from app.models.user import User
from app.services.reasonability import ReasonabilityAnalysisService
from app.services.project import ProjectService
from app.utils.price_reasonability import RiskLevel, PriceStatus

router = APIRouter()


class ReasonabilityAnalysisRequest(BaseModel):
    """合理性分析请求模型"""
    force_reanalyze: bool = Field(False, description="是否强制重新分析")
    detection_sensitivity: float = Field(0.1, ge=0.01, le=1.0, description="异常检测敏感度")


class ManualAdjustmentRequest(BaseModel):
    """人工调整请求模型"""
    is_reasonable: bool = Field(..., description="是否合理")
    risk_level: str = Field(..., description="风险等级")
    notes: str = Field(..., min_length=1, max_length=500, description="调整说明")


@router.post("/{project_id}/analyze-reasonability")
async def analyze_project_price_reasonability(
    project_id: int,
    request: ReasonabilityAnalysisRequest,
    current_user: SimpleUser = Depends(require_cost_engineer()),
    db: AsyncSession = Depends(get_db)
):
    """分析项目材料价格合理性"""
    
    # 验证项目存在和权限
    project = await ProjectService.get_project_by_id(db, project_id, current_user)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    try:
        analysis_service = ReasonabilityAnalysisService()
        result = await analysis_service.analyze_project_price_reasonability(
            db=db,
            project_id=project_id,
            force_reanalyze=request.force_reanalyze,
            detection_sensitivity=request.detection_sensitivity
        )
        
        return {
            "message": "价格合理性分析完成",
            "analysis_result": result
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析失败: {str(e)}"
        )


@router.get("/{project_id}/unreasonable-materials")
async def get_unreasonable_materials(
    project_id: int,
    risk_level: Optional[str] = Query(None, description="风险等级筛选"),
    price_status: Optional[str] = Query(None, description="价格状态筛选"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取价格不合理的材料列表"""
    
    # 验证项目存在和权限
    project = await ProjectService.get_project_by_id(db, project_id, current_user)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 验证参数
    risk_level_enum = None
    if risk_level:
        try:
            risk_level_enum = RiskLevel(risk_level)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的风险等级: {risk_level}"
            )
    
    price_status_enum = None
    if price_status:
        try:
            price_status_enum = PriceStatus(price_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的价格状态: {price_status}"
            )
    
    try:
        analysis_service = ReasonabilityAnalysisService()
        unreasonable_materials = await analysis_service.get_unreasonable_materials(
            db=db,
            project_id=project_id,
            risk_level=risk_level_enum,
            price_status=price_status_enum,
            skip=skip,
            limit=limit
        )
        
        return {
            "project_id": project_id,
            "unreasonable_materials": unreasonable_materials,
            "total": len(unreasonable_materials)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取不合理材料列表失败: {str(e)}"
        )


@router.get("/{project_id}/risk-summary")
async def get_project_risk_summary(
    project_id: int,
    current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取项目风险汇总"""
    
    # 验证项目存在和权限
    project = await ProjectService.get_project_by_id(db, project_id, current_user)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    try:
        analysis_service = ReasonabilityAnalysisService()
        risk_summary = await analysis_service.get_project_risk_summary(
            db=db,
            project_id=project_id
        )
        
        return risk_summary
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取风险汇总失败: {str(e)}"
        )


@router.post("/materials/{material_id}/adjust")
async def manual_adjust_reasonability(
    material_id: int,
    request: ManualAdjustmentRequest,
    current_user: SimpleUser = Depends(require_cost_engineer()),
    db: AsyncSession = Depends(get_db)
):
    """人工调整材料价格合理性判断"""
    
    # 验证风险等级
    try:
        risk_level = RiskLevel(request.risk_level)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的风险等级: {request.risk_level}"
        )
    
    try:
        analysis_service = ReasonabilityAnalysisService()
        success = await analysis_service.manual_adjust_reasonability(
            db=db,
            material_id=material_id,
            is_reasonable=request.is_reasonable,
            risk_level=risk_level,
            notes=request.notes,
            user_id=current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="材料分析记录不存在"
            )
        
        return {
            "message": "合理性判断调整成功",
            "material_id": material_id,
            "adjusted_by": current_user.username
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"调整合理性判断失败: {str(e)}"
        )


@router.get("/risk-levels")
async def get_risk_levels(
    current_user: SimpleUser = Depends(get_current_active_user)
):
    """获取所有风险等级选项"""
    
    return {
        "risk_levels": [
            {"value": RiskLevel.LOW.value, "label": "低风险", "description": "价格在合理范围内"},
            {"value": RiskLevel.MEDIUM.value, "label": "中风险", "description": "价格略有偏差"},
            {"value": RiskLevel.HIGH.value, "label": "高风险", "description": "价格明显偏离正常范围"},
            {"value": RiskLevel.CRITICAL.value, "label": "严重风险", "description": "价格异常，需要立即关注"}
        ]
    }


@router.get("/price-statuses")
async def get_price_statuses(
    current_user: SimpleUser = Depends(get_current_active_user)
):
    """获取所有价格状态选项"""
    
    return {
        "price_statuses": [
            {"value": PriceStatus.REASONABLE.value, "label": "合理", "description": "价格在预期范围内"},
            {"value": PriceStatus.OVERPRICED.value, "label": "价格偏高", "description": "价格高于市场水平"},
            {"value": PriceStatus.UNDERPRICED.value, "label": "价格偏低", "description": "价格低于市场水平"},
            {"value": PriceStatus.ABNORMAL.value, "label": "异常价格", "description": "价格异常偏离正常范围"},
            {"value": PriceStatus.UNKNOWN.value, "label": "无法判断", "description": "缺乏足够信息进行判断"}
        ]
    }


@router.get("/{project_id}/reasonability-statistics")
async def get_reasonability_statistics(
    project_id: int,
    current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取项目合理性分析统计信息"""
    
    # 验证项目存在和权限
    project = await ProjectService.get_project_by_id(db, project_id, current_user)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    try:
        analysis_service = ReasonabilityAnalysisService()
        
        # 获取基本统计
        risk_summary = await analysis_service.get_project_risk_summary(db, project_id)
        
        # 获取各类型材料数量
        reasonable_materials = await analysis_service.get_unreasonable_materials(
            db, project_id, price_status=PriceStatus.REASONABLE, limit=1000
        )
        
        overpriced_materials = await analysis_service.get_unreasonable_materials(
            db, project_id, price_status=PriceStatus.OVERPRICED, limit=1000
        )
        
        underpriced_materials = await analysis_service.get_unreasonable_materials(
            db, project_id, price_status=PriceStatus.UNDERPRICED, limit=1000
        )
        
        abnormal_materials = await analysis_service.get_unreasonable_materials(
            db, project_id, price_status=PriceStatus.ABNORMAL, limit=1000
        )
        
        return {
            "project_id": project_id,
            "risk_summary": risk_summary,
            "status_distribution": {
                "reasonable": len(reasonable_materials),
                "overpriced": len(overpriced_materials), 
                "underpriced": len(underpriced_materials),
                "abnormal": len(abnormal_materials)
            },
            "analysis_completion": {
                "total_materials": risk_summary["total_materials"],
                "analyzed_materials": risk_summary["total_materials"],
                "completion_rate": 100.0 if risk_summary["total_materials"] > 0 else 0.0
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )