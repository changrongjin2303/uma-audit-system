from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.simple_auth import get_current_active_user, require_cost_engineer, SimpleUser
from app.models.user import User
from app.models.analysis import AnalysisStatus
from app.services.price_analysis import PriceAnalysisService
from app.services.ai_analysis import AIProvider
from app.services.project import ProjectService

router = APIRouter()


class AnalyzeProjectRequest(BaseModel):
    """分析项目请求模型"""
    material_ids: Optional[List[int]] = Field(None, description="指定要分析的材料ID列表，为空则分析所有材料")
    batch_size: int = Field(20, ge=1, le=100, description="批量处理大小")
    force_reanalyze: bool = Field(False, description="是否强制重新分析")
    preferred_provider: Optional[str] = Field(None, description="首选AI服务提供商")


class AnalyzeMaterialRequest(BaseModel):
    """分析材料请求模型"""
    preferred_provider: Optional[str] = Field(None, description="首选AI服务提供商")
    force_reanalyze: bool = Field(False, description="是否强制重新分析")


@router.post("/{project_id}/analyze")
async def analyze_project_materials(
    project_id: int,
    request: AnalyzeProjectRequest,
    # 开发环境暂时移除认证要求
    # # 开发环境暂时移除认证要求
    # current_user: SimpleUser = Depends(require_cost_engineer()),
    db: AsyncSession = Depends(get_db)
):
    """批量分析项目材料价格"""
    
    # 验证项目存在和权限
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 验证AI服务提供商
    preferred_provider = None
    if request.preferred_provider:
        try:
            preferred_provider = AIProvider(request.preferred_provider)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的AI服务提供商: {request.preferred_provider}"
            )
    
    try:
        analysis_service = PriceAnalysisService()
        result = await analysis_service.analyze_project_materials(
            db=db,
            project_id=project_id,
            material_ids=request.material_ids,
            batch_size=request.batch_size,
            force_reanalyze=request.force_reanalyze,
            preferred_provider=preferred_provider
        )
        
        return {
            "message": "材料价格分析完成",
            "result": result
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析失败: {str(e)}"
        )


class AnalyzePricedMaterialsRequest(BaseModel):
    """分析市场信息价材料请求模型"""
    material_ids: List[int] = Field(..., description="要分析的材料ID列表")
    batch_size: int = Field(10, ge=1, le=100, description="批量处理大小")


@router.post("/{project_id}/analyze-priced-materials")
async def analyze_priced_materials(
    project_id: int,
    request: AnalyzePricedMaterialsRequest,
    # 开发环境暂时移除认证要求
    # current_user: SimpleUser = Depends(require_cost_engineer()),
    db: AsyncSession = Depends(get_db)
):
    """分析市场信息价材料价格差异"""
    
    # 验证项目存在和权限
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    try:
        from app.services.priced_material_analysis import PricedMaterialAnalysisService
        
        analysis_service = PricedMaterialAnalysisService()
        result = await analysis_service.analyze_priced_materials(
            db=db,
            project_id=project_id,
            material_ids=request.material_ids,
            batch_size=request.batch_size
        )
        
        return {
            "message": "市场信息价材料分析完成",
            "analyzed_count": result["analyzed_count"],
            "differences_count": result["differences_count"],
            "result": result
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"市场信息价材料分析失败: {str(e)}"
        )


@router.post("/materials/{material_id}/analyze")
async def analyze_single_material(
    material_id: int,
    request: AnalyzeMaterialRequest,
    # 开发环境暂时移除认证要求
    # current_user: SimpleUser = Depends(require_cost_engineer()),
    db: AsyncSession = Depends(get_db)
):
    """分析单个材料价格"""
    
    # 验证AI服务提供商
    preferred_provider = None
    if request.preferred_provider:
        try:
            preferred_provider = AIProvider(request.preferred_provider)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的AI服务提供商: {request.preferred_provider}"
            )
    
    try:
        analysis_service = PriceAnalysisService()
        result = await analysis_service.analyze_single_material(
            db=db,
            material_id=material_id,
            preferred_provider=preferred_provider,
            force_reanalyze=request.force_reanalyze
        )
        
        return {
            "message": "材料价格分析完成",
            "result": result
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析失败: {str(e)}"
        )


@router.get("/{project_id}/analysis-results")
async def get_analysis_results(
    project_id: int,
    status: Optional[str] = Query(None, description="分析状态筛选"),
    is_reasonable: Optional[bool] = Query(None, description="价格合理性筛选"),
    risk_level: Optional[str] = Query(None, description="风险等级筛选"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    # 开发环境暂时移除认证要求
    # current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取项目分析结果"""
    
    # 验证项目存在和权限
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 验证状态参数
    analysis_status = None
    if status:
        try:
            analysis_status = AnalysisStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的分析状态: {status}"
            )
    
    try:
        analysis_service = PriceAnalysisService()
        results = await analysis_service.get_analysis_results(
            db=db,
            project_id=project_id,
            status=analysis_status,
            is_reasonable=is_reasonable,
            risk_level=risk_level,
            skip=skip,
            limit=limit
        )
        
        return {
            "project_id": project_id,
            "results": results,
            "total": len(results)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分析结果失败: {str(e)}"
        )


@router.get("/{project_id}/analysis-statistics")
async def get_analysis_statistics(
    project_id: int,
    # 开发环境暂时移除认证要求
    # current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取项目分析统计信息"""
    
    # 验证项目存在和权限
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    try:
        analysis_service = PriceAnalysisService()
        statistics = await analysis_service.get_analysis_statistics(
            db=db,
            project_id=project_id
        )
        
        return statistics
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )


@router.get("/{project_id}/priced-materials-analysis")
async def get_priced_materials_analysis(
    project_id: int,
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(1000, ge=1, le=1000, description="返回的记录数"),
    # 开发环境暂时移除认证要求
    # current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取项目市场信息价材料分析结果"""
    
    # 验证项目存在和权限
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    try:
        from app.models.analysis import PriceAnalysis
        from app.models.project import ProjectMaterial
        from sqlalchemy import select, and_, func
        
        # 从数据库获取已保存的市场信息价分析结果
        stmt = select(
            PriceAnalysis.material_id,
            PriceAnalysis.api_response,
            PriceAnalysis.analysis_reasoning,
            PriceAnalysis.created_at,
            ProjectMaterial.material_name,
            ProjectMaterial.specification,
            ProjectMaterial.unit,
            ProjectMaterial.quantity
        ).select_from(
            PriceAnalysis.__table__.join(
                ProjectMaterial, PriceAnalysis.material_id == ProjectMaterial.id
            )
        ).where(
            and_(
                ProjectMaterial.project_id == project_id,
                PriceAnalysis.analysis_model == "guided_price_comparison"
            )
        ).offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        analysis_records = result.all()
        
        # 转换为前端需要的格式
        results = []
        for record in analysis_records:
            api_data = record.api_response or {}
            base_info = api_data.get('base_material_info', {})
            
            result_item = {
                "material_id": record.material_id,
                "material_name": record.material_name or "",
                "specification": record.specification or "",
                "unit": record.unit or "",
                "quantity": float(record.quantity or 0),
                "project_unit_price": api_data.get('project_unit_price', 0),
                "base_unit_price": api_data.get('base_unit_price', 0),
                "base_price_including_tax": api_data.get('base_price_including_tax', 0),
                "base_price_excluding_tax": api_data.get('base_price_excluding_tax', 0),
                "unit_price_difference": api_data.get('unit_price_difference', 0),
                "total_price_difference": api_data.get('total_price_difference', 0),
                "price_difference_rate": api_data.get('price_difference_rate', 0),
                "has_difference": api_data.get('has_difference', False),
                "difference_level": api_data.get('difference_level', 'normal'),
                "base_material_name": base_info.get('name', ''),
                "base_specification": base_info.get('specification', ''),
                "source_type": base_info.get('source_type', ''),
                "region": base_info.get('region', ''),
                "analyzed_at": record.created_at.isoformat() if record.created_at else None
            }
            results.append(result_item)
        
        # 获取总数
        count_stmt = select(func.count(PriceAnalysis.id)).select_from(
            PriceAnalysis.__table__.join(
                ProjectMaterial, PriceAnalysis.material_id == ProjectMaterial.id
            )
        ).where(
            and_(
                ProjectMaterial.project_id == project_id,
                PriceAnalysis.analysis_model == "guided_price_comparison"
            )
        )
        count_result = await db.execute(count_stmt)
        total = count_result.scalar() or 0
        
        return {
            "project_id": project_id,
            "results": results,
            "total": total
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取市场信息价材料分析结果失败: {str(e)}"
        )


@router.get("/projects-with-results")
async def get_projects_with_analysis_results(
    # 开发环境暂时移除认证要求
    # current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取有分析结果的项目列表"""
    
    try:
        from sqlalchemy import select, func
        from app.models.project import Project
        from app.models.analysis import PriceAnalysis
        
        # 查询有分析结果的项目
        from app.models.project import ProjectMaterial
        
        stmt = select(
            Project.id,
            Project.name,
            Project.description,
            Project.project_type,
            func.count(PriceAnalysis.id).label('analysis_count'),
            func.max(PriceAnalysis.analyzed_at).label('last_analyzed_at')
        ).select_from(
            Project.__table__
            .join(ProjectMaterial, Project.id == ProjectMaterial.project_id)
            .join(PriceAnalysis, ProjectMaterial.id == PriceAnalysis.material_id)
        ).where(
            PriceAnalysis.status == AnalysisStatus.COMPLETED
        ).group_by(
            Project.id, Project.name, Project.description, Project.project_type
        ).order_by(
            func.max(PriceAnalysis.analyzed_at).desc()
        )
        
        result = await db.execute(stmt)
        projects = result.all()
        
        # 格式化结果并添加详细统计信息
        formatted_projects = []
        for project in projects:
            # 获取项目的总材料数量
            total_materials_stmt = select(func.count(ProjectMaterial.id)).where(
                ProjectMaterial.project_id == project.id
            )
            total_materials_result = await db.execute(total_materials_stmt)
            total_materials = total_materials_result.scalar()
            
            # 获取合理和风险材料的数量
            reasonable_stmt = select(func.count(PriceAnalysis.id)).select_from(
                ProjectMaterial.__table__.join(
                    PriceAnalysis, ProjectMaterial.id == PriceAnalysis.material_id
                )
            ).where(
                ProjectMaterial.project_id == project.id,
                PriceAnalysis.status == AnalysisStatus.COMPLETED,
                PriceAnalysis.is_reasonable == True
            )
            reasonable_result = await db.execute(reasonable_stmt)
            reasonable_count = reasonable_result.scalar()
            
            risk_stmt = select(func.count(PriceAnalysis.id)).select_from(
                ProjectMaterial.__table__.join(
                    PriceAnalysis, ProjectMaterial.id == PriceAnalysis.material_id
                )
            ).where(
                ProjectMaterial.project_id == project.id,
                PriceAnalysis.status == AnalysisStatus.COMPLETED,
                PriceAnalysis.is_reasonable == False
            )
            risk_result = await db.execute(risk_stmt)
            risk_count = risk_result.scalar()
            
            formatted_projects.append({
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "project_type": project.project_type,
                "analysis_count": project.analysis_count,
                "total_materials": total_materials,
                "reasonable_count": reasonable_count or 0,
                "risk_count": risk_count or 0,
                "last_analyzed_at": project.last_analyzed_at.isoformat() if project.last_analyzed_at else None
            })
        
        return {
            "projects": formatted_projects,
            "total_count": len(formatted_projects)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取项目列表失败: {str(e)}"
        )


@router.get("/ai-services/available")
async def get_available_ai_services(
    # 开发环境暂时移除认证要求
    # current_user: SimpleUser = Depends(get_current_active_user)
):
    """获取可用的AI服务列表"""
    
    try:
        analysis_service = PriceAnalysisService()
        providers = analysis_service.ai_manager.get_available_providers()
        
        return {
            "available_providers": providers,
            "total_count": len(providers)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取AI服务信息失败: {str(e)}"
        )


@router.post("/ai-services/test")
async def test_ai_service(
    provider: str,
    # 开发环境暂时移除认证要求
    # current_user: SimpleUser = Depends(require_cost_engineer()),
    db: AsyncSession = Depends(get_db)
):
    """测试AI服务可用性"""
    
    # 验证AI服务提供商
    try:
        ai_provider = AIProvider(provider)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的AI服务提供商: {provider}"
        )
    
    try:
        analysis_service = PriceAnalysisService()
        test_result = await analysis_service.ai_manager.test_service(ai_provider)
        
        return {
            "provider": provider,
            "test_result": test_result
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"测试AI服务失败: {str(e)}"
        )


@router.get("/materials/{material_id}/analysis")
async def get_material_analysis(
    material_id: int,
    # 开发环境暂时移除认证要求
    # current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取单个材料的分析结果"""
    
    try:
        analysis_service = PriceAnalysisService()
        analysis = await analysis_service._get_existing_analysis(db, material_id)
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="材料分析结果不存在"
            )
        
        return {
            "material_id": material_id,
            "analysis": analysis_service._format_analysis_result_detailed(analysis)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分析结果失败: {str(e)}"
        )


@router.delete("/materials/{material_id}/analysis")
async def delete_material_analysis(
    material_id: int,
    # 开发环境暂时移除认证要求
    # current_user: SimpleUser = Depends(require_cost_engineer()),
    db: AsyncSession = Depends(get_db)
):
    """删除材料分析结果"""
    
    try:
        analysis_service = PriceAnalysisService()
        analysis = await analysis_service._get_existing_analysis(db, material_id)
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="材料分析结果不存在"
            )
        
        await db.delete(analysis)
        await db.commit()
        
        return {
            "message": "分析结果已删除",
            "material_id": material_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除分析结果失败: {str(e)}"
        )


@router.get("/materials/{material_id}/analysis-detail")
async def get_material_analysis_detail(
    material_id: int,
    # 开发环境暂时移除认证要求
    # current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取单个材料的详细分析结果，包括原始材料信息、匹配的市场信息价材料信息和分析结果"""
    
    try:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from app.models.project import ProjectMaterial
        from app.models.material import BaseMaterial
        from app.models.analysis import PriceAnalysis
        
        # 获取项目材料信息
        query = select(ProjectMaterial).where(ProjectMaterial.id == material_id)
        result = await db.execute(query)
        project_material = result.scalar_one_or_none()
        
        if not project_material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目材料不存在"
            )
        
        # 获取分析结果
        analysis = None
        analysis_query = select(PriceAnalysis).where(
            PriceAnalysis.material_id == material_id
        ).order_by(PriceAnalysis.created_at.desc())
        analysis_result = await db.execute(analysis_query)
        analysis = analysis_result.scalar_one_or_none()
        
        # 获取项目信息
        from app.models.project import Project
        project_query = select(Project).where(Project.id == project_material.project_id)
        project_result = await db.execute(project_query)
        project = project_result.scalar_one_or_none()
        
        # 获取匹配的市场信息价材料信息
        matched_base_material = None
        if project_material.matched_material_id:  # 使用正确的字段名
            base_material_query = select(BaseMaterial).where(
                BaseMaterial.id == project_material.matched_material_id
            )
            base_material_result = await db.execute(base_material_query)
            matched_base_material = base_material_result.scalar_one_or_none()
        
        # 构建详细响应数据
        detail_data = {
            "material_id": material_id,
            "project_material": {
                "id": project_material.id,
                "material_name": project_material.material_name,
                "specification": project_material.specification,
                "unit": project_material.unit,
                "quantity": float(project_material.quantity) if project_material.quantity else None,
                "unit_price": float(project_material.unit_price) if project_material.unit_price else None,
                "total_price": float(project_material.total_price) if project_material.total_price else None,
                "material_code": getattr(project_material, 'material_code', None),
                "brand": getattr(project_material, 'brand', None),
                "category": project_material.category,
                "subcategory": project_material.subcategory,
                "remarks": project_material.notes,
                "has_matched_base_material": project_material.matched_material_id is not None,
                "matched_base_material_id": project_material.matched_material_id,
                "created_at": project_material.created_at.isoformat() if project_material.created_at else None,
                "updated_at": None
            },
            "project_info": {
                "id": project.id,
                "name": project.name,
                "location": project.location,
                "project_type": project.project_type
            } if project else None,
            "matched_base_material": None,
            "analysis_result": None
        }
        
        # 添加匹配的市场信息价材料信息
        if matched_base_material:
            detail_data["matched_base_material"] = {
                "id": matched_base_material.id,
                "name": matched_base_material.name,
                "specification": matched_base_material.specification,
                "unit": matched_base_material.unit,
                "price": float(matched_base_material.price) if matched_base_material.price else None,
                "price_type": matched_base_material.price_type,
                "category": matched_base_material.category,
                "subcategory": matched_base_material.subcategory,
                "material_code": matched_base_material.material_code,
                "brand": getattr(matched_base_material, 'brand', None),
                "region": matched_base_material.region,
                "source": matched_base_material.source,
                "effective_date": matched_base_material.effective_date.isoformat() if matched_base_material.effective_date else None,
                "created_at": matched_base_material.created_at.isoformat() if matched_base_material.created_at else None,
                "updated_at": matched_base_material.updated_at.isoformat() if matched_base_material.updated_at else None
            }
        
        # 添加分析结果
        if analysis:
            api_response = analysis.api_response or {}
            total_price_difference = api_response.get('total_price_difference')
            unit_price_difference = api_response.get('unit_price_difference')
            analysis_quantity = api_response.get('quantity') or detail_data["project_material"].get('quantity')
            analysis_unit = api_response.get('unit') or detail_data["project_material"].get('unit')

            detail_data["analysis_result"] = {
                "id": analysis.id,
                "status": analysis.status,
                "predicted_price_min": float(analysis.predicted_price_min) if analysis.predicted_price_min else None,
                "predicted_price_max": float(analysis.predicted_price_max) if analysis.predicted_price_max else None,
                "predicted_price_avg": float(analysis.predicted_price_avg) if analysis.predicted_price_avg else None,
                "confidence_score": float(analysis.confidence_score) if analysis.confidence_score else None,
                "is_reasonable": analysis.is_reasonable,
                "price_variance": float(analysis.price_variance) if analysis.price_variance else None,
                "risk_level": analysis.risk_level,
                "analysis_model": analysis.analysis_model,
                "analysis_prompt": analysis.analysis_prompt,
                "data_sources": analysis.data_sources,
                "market_data": analysis.market_data,
                "reference_prices": analysis.reference_prices,
                "analysis_reasoning": analysis.analysis_reasoning,
                "risk_factors": analysis.risk_factors,
                "recommendations": analysis.recommendations,
                "analysis_date": analysis.analyzed_at.isoformat() if analysis.analyzed_at else None,
                "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
                "updated_at": analysis.updated_at.isoformat() if analysis.updated_at else None,
                "api_response": api_response,
                "total_price_difference": float(total_price_difference) if total_price_difference is not None else None,
                "unit_price_difference": float(unit_price_difference) if unit_price_difference is not None else None,
                "quantity": float(analysis_quantity) if analysis_quantity is not None else None,
                "unit": analysis_unit
            }
        
        return {
            "code": 200,
            "message": "获取材料分析详情成功",
            "data": detail_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取材料分析详情错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取材料分析详情失败: {str(e)}"
        )
