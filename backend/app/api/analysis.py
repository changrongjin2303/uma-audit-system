from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from loguru import logger

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
    material_ids: Optional[List[int]] = Field(None, description="要分析的材料ID列表，为空则分析所有材料")
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
    material_name: Optional[str] = Query(None, description="材料名称筛选"),
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
    indeterminate = False
    
    if status:
        if status == 'indeterminate':
            indeterminate = True
            analysis_status = AnalysisStatus.COMPLETED
        else:
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
            material_name=material_name,
            skip=skip,
            limit=limit,
            indeterminate=indeterminate
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
    status: Optional[str] = Query(None, description="分析状态筛选"),
    risk_level: Optional[str] = Query(None, description="风险等级筛选"),
    material_name: Optional[str] = Query(None, description="材料名称筛选"),
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
    
    # 验证状态参数
    analysis_status = None
    if status:
        try:
            analysis_status = AnalysisStatus(status)
        except ValueError:
            pass  # 如果状态无效，忽略该筛选条件

    try:
        from app.models.analysis import PriceAnalysis, PriceAnalysisHistory
        from app.models.project import ProjectMaterial
        from sqlalchemy import select, and_, func
        
        # 构建筛选条件
        conditions = [
            ProjectMaterial.project_id == project_id,
            PriceAnalysis.analysis_model == "guided_price_comparison"
        ]
        
        if analysis_status:
            conditions.append(PriceAnalysis.status == analysis_status)
            
        if risk_level:
            conditions.append(PriceAnalysis.risk_level == risk_level)

        if material_name:
            conditions.append(ProjectMaterial.material_name.ilike(f"%{material_name}%"))
        
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
            and_(*conditions)
        ).offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        analysis_records = result.all()
        
        # 转换为前端需要的格式
        results = []
        for record in analysis_records:
            try:
                # 安全地解析 JSON 数据
                api_data = record.api_response or {}
                if isinstance(api_data, str):
                    import json
                    try:
                        api_data = json.loads(api_data)
                    except json.JSONDecodeError:
                        api_data = {}
                
                base_info = api_data.get('base_material_info', {})
                if not isinstance(base_info, dict):
                    base_info = {}
                
                # 安全地转换数值类型
                def safe_float(value, default=0.0):
                    try:
                        return float(value) if value is not None else default
                    except (ValueError, TypeError):
                        return default
                
                result_item = {
                    "material_id": record.material_id,
                    "material_name": record.material_name or "",
                    "specification": record.specification or "",
                    "unit": record.unit or "",
                    "base_unit": api_data.get('base_unit') or record.unit or "",  # 基期材料单位，用于单位转换
                    "quantity": safe_float(record.quantity, 0),
                    "project_unit_price": safe_float(api_data.get('project_unit_price'), 0),
                    "base_unit_price": safe_float(api_data.get('base_unit_price'), 0),
                    "contract_average_price": safe_float(api_data.get('base_unit_price'), 0),  # 合同期平均价，同base_unit_price
                    "base_price_including_tax": safe_float(api_data.get('base_price_including_tax'), 0),
                    "base_price_excluding_tax": safe_float(api_data.get('base_price_excluding_tax'), 0),
                    "original_base_price": safe_float(api_data.get('original_base_price'), 0),  # 原始基期信息价
                    "unit_price_difference": safe_float(api_data.get('unit_price_difference'), 0),
                    "total_price_difference": safe_float(api_data.get('total_price_difference'), 0),
                    "price_difference_rate": safe_float(api_data.get('price_difference_rate'), 0),
                    "has_difference": bool(api_data.get('has_difference', False)),
                    "difference_level": api_data.get('difference_level', 'normal') or 'normal',
                    "base_material_name": base_info.get('name', '') if isinstance(base_info, dict) else '',
                    "base_specification": base_info.get('specification', '') if isinstance(base_info, dict) else '',
                    "source_type": base_info.get('source_type', '') if isinstance(base_info, dict) else '',
                    "region": base_info.get('region', '') if isinstance(base_info, dict) else '',
                    "analyzed_at": record.created_at.isoformat() if record.created_at else None
                }
                results.append(result_item)
            except Exception as e:
                # 如果某条记录处理失败，记录日志但继续处理其他记录
                logger.warning(f"处理材料 {record.material_id} 的分析结果时出错: {e}")
                continue
        
        # 获取总数
        count_stmt = select(func.count(PriceAnalysis.id)).select_from(
            PriceAnalysis.__table__.join(
                ProjectMaterial, PriceAnalysis.material_id == ProjectMaterial.id
            )
        ).where(
            and_(*conditions)
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
            
            # 获取无法判定(Indeterminate)的数量: status=COMPLETED and is_reasonable is None
            indeterminate_stmt = select(func.count(PriceAnalysis.id)).select_from(
                ProjectMaterial.__table__.join(
                    PriceAnalysis, ProjectMaterial.id == PriceAnalysis.material_id
                )
            ).where(
                ProjectMaterial.project_id == project.id,
                PriceAnalysis.status == AnalysisStatus.COMPLETED,
                PriceAnalysis.is_reasonable == None
            )
            indeterminate_result = await db.execute(indeterminate_stmt)
            indeterminate_count = indeterminate_result.scalar()

            # 获取失败(Failed)的数量: status=FAILED
            failed_stmt = select(func.count(PriceAnalysis.id)).select_from(
                ProjectMaterial.__table__.join(
                    PriceAnalysis, ProjectMaterial.id == PriceAnalysis.material_id
                )
            ).where(
                ProjectMaterial.project_id == project.id,
                PriceAnalysis.status == AnalysisStatus.FAILED
            )
            failed_result = await db.execute(failed_stmt)
            failed_count = failed_result.scalar()
            
            formatted_projects.append({
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "project_type": project.project_type,
                "analysis_count": project.analysis_count,
                "total_materials": total_materials,
                "reasonable_count": reasonable_count or 0,
                "risk_count": risk_count or 0,
                "indeterminate_count": indeterminate_count or 0,
                "failed_count": failed_count or 0,
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
        from sqlalchemy import select, and_, or_
        from sqlalchemy.orm import selectinload
        from app.models.project import ProjectMaterial
        from app.models.material import BaseMaterial
        from app.models.analysis import PriceAnalysis, PriceAnalysisHistory
        
        # 获取项目材料信息
        query = select(ProjectMaterial).where(ProjectMaterial.id == material_id)
        result = await db.execute(query)
        project_material = result.scalar_one_or_none()
        
        if not project_material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目材料不存在"
            )
        
        # 获取分析结果（最新的）
        analysis = None
        analysis_query = select(PriceAnalysis).where(
            PriceAnalysis.material_id == material_id
        ).order_by(PriceAnalysis.created_at.desc())
        analysis_result = await db.execute(analysis_query)
        analysis = analysis_result.scalar_one_or_none()
        
        # 获取所有分析历史记录（用于分析历史时间线）
        all_analyses = []
        history_records = []
        try:
            # 优先从历史表获取（每次分析一条记录）
            history_query = select(PriceAnalysisHistory).where(
                PriceAnalysisHistory.material_id == material_id
            ).order_by(PriceAnalysisHistory.created_at.desc())
            history_result = await db.execute(history_query)
            history_records = history_result.scalars().all()
        except Exception as e:
            # 历史表可能尚未创建或其他错误，记录日志后回退到主表
            logger.warning(f"获取价格分析历史表记录失败，将回退到主表: {str(e)}")
            history_records = []

        # 兼容：如果历史表为空，则从主分析表中按时间倒序构造历史
        if not history_records:
            try:
                all_analyses_query = select(PriceAnalysis).where(
                    PriceAnalysis.material_id == material_id
                ).order_by(PriceAnalysis.created_at.desc())
                all_analyses_result = await db.execute(all_analyses_query)
                all_analyses = all_analyses_result.scalars().all()
            except Exception as e:
                logger.warning(f"获取分析历史记录失败: {str(e)}")
                all_analyses = []
        
        # 获取项目信息
        from app.models.project import Project
        project_query = select(Project).where(Project.id == project_material.project_id)
        project_result = await db.execute(project_query)
        project = project_result.scalar_one_or_none()
        
        # 日期格式化帮助函数
        def normalize_year_month(value: Optional[str]) -> Optional[str]:
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
        
        def year_month_tuple(value: Optional[str]) -> Optional[tuple]:
            norm = normalize_year_month(value)
            if not norm:
                return None
            parts = norm.split('-')
            if len(parts) != 2:
                return None
            try:
                return int(parts[0]), int(parts[1])
            except ValueError:
                return None
        
        def compare_year_month(a: Optional[str], b: Optional[str]) -> Optional[int]:
            tuple_a = year_month_tuple(a)
            tuple_b = year_month_tuple(b)
            if not tuple_a or not tuple_b:
                return None
            if tuple_a < tuple_b:
                return -1
            if tuple_a > tuple_b:
                return 1
            return 0
        
        def is_within_contract(price_date: Optional[str], start_tuple: Optional[tuple], end_tuple: Optional[tuple]) -> bool:
            ym_tuple = year_month_tuple(price_date)
            if not ym_tuple:
                return True
            if start_tuple and ym_tuple < start_tuple:
                return False
            if end_tuple and ym_tuple > end_tuple:
                return False
            return True
        
        # 基期与合同工期信息
        preferred_price_date = None
        contract_start_date = None
        contract_end_date = None
        preferred_price_tuple = None
        contract_start_tuple = None
        contract_end_tuple = None
        if project:
            preferred_price_date = normalize_year_month(project.base_price_date or project.price_base_date)
            preferred_price_tuple = year_month_tuple(preferred_price_date)
            contract_start_date = normalize_year_month(project.contract_start_date)
            contract_end_date = normalize_year_month(project.contract_end_date)
            contract_start_tuple = year_month_tuple(contract_start_date)
            contract_end_tuple = year_month_tuple(contract_end_date)
        
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
            "matched_base_materials": [],
            "analysis_result": None
        }
        
        # 添加匹配的市场信息价材料信息
        def serialize_base_material(base_material, preferred_date=None, matched_id=None):
            is_current = False
            if preferred_date and base_material.price_date:
                is_current = normalize_year_month(base_material.price_date) == preferred_date
            elif matched_id:
                is_current = base_material.id == matched_id
                
            return {
                "id": base_material.id,
                "name": base_material.name,
                "specification": base_material.specification,
                "unit": base_material.unit,
                "price": float(base_material.price) if base_material.price is not None else None,
                "price_including_tax": float(base_material.price_including_tax) if base_material.price_including_tax is not None else None,
                "price_excluding_tax": float(base_material.price_excluding_tax) if base_material.price_excluding_tax is not None else None,
                "price_type": base_material.price_type,
                "price_date": base_material.price_date,
                "issue_period": (
                    f"{base_material.price_date.split('-')[0]}年{base_material.price_date.split('-')[1].zfill(2)}月"
                    if base_material.price_date else None
                ),
                "category": base_material.category,
                "subcategory": base_material.subcategory,
                "material_code": base_material.material_code,
                "brand": getattr(base_material, 'brand', None),
                "region": base_material.region,
                "source": base_material.source,
                "price_source": getattr(base_material, 'price_source', None),
                "effective_date": base_material.effective_date.isoformat() if base_material.effective_date else None,
                "created_at": base_material.created_at.isoformat() if base_material.created_at else None,
                "updated_at": base_material.updated_at.isoformat() if base_material.updated_at else None,
                "is_current_match": is_current
            }

        if matched_base_material:
            # 查找同一材料的其他期数信息价（优先使用材料编码，其次名称/规格/单位/地区）
            related_conditions = []
            if matched_base_material.material_code:
                related_conditions.append(BaseMaterial.material_code == matched_base_material.material_code)
            else:
                related_conditions.append(BaseMaterial.name == matched_base_material.name)
                if matched_base_material.specification:
                    related_conditions.append(BaseMaterial.specification == matched_base_material.specification)
                else:
                    related_conditions.append(
                        or_(
                            BaseMaterial.specification.is_(None),
                            BaseMaterial.specification == ""
                        )
                    )
                if matched_base_material.unit:
                    related_conditions.append(BaseMaterial.unit == matched_base_material.unit)
                if matched_base_material.region:
                    related_conditions.append(BaseMaterial.region == matched_base_material.region)
                elif getattr(matched_base_material, 'province', None):
                    related_conditions.append(BaseMaterial.province == matched_base_material.province)
                if matched_base_material.price_type:
                    related_conditions.append(BaseMaterial.price_type == matched_base_material.price_type)
            
            related_query = select(BaseMaterial).where(
                and_(*related_conditions)
            ).order_by(
                BaseMaterial.price_date.desc(),
                BaseMaterial.effective_date.desc()
            )

            related_result = await db.execute(related_query)
            related_materials_all = related_result.scalars().all()

            if not related_materials_all:
                related_materials_all = [matched_base_material]

            # 选择基于基期信息价日期的当前显示材料
            selected_material = None
            if preferred_price_tuple:
                selected_material = next(
                    (
                        material
                        for material in related_materials_all
                        if year_month_tuple(material.price_date) == preferred_price_tuple
                    ),
                    None
                )
                if not selected_material:
                    earlier_candidates = [
                        material for material in related_materials_all
                        if year_month_tuple(material.price_date)
                        and year_month_tuple(material.price_date) <= preferred_price_tuple
                    ]
                    if earlier_candidates:
                        selected_material = max(
                            earlier_candidates,
                            key=lambda m: year_month_tuple(m.price_date)
                        )

            if not selected_material:
                selected_material = matched_base_material if matched_base_material else related_materials_all[0]

            display_materials = [
                material for material in related_materials_all
                if is_within_contract(material.price_date, contract_start_tuple, contract_end_tuple)
            ]

            if not display_materials:
                display_materials = related_materials_all.copy()

            if selected_material and all(material.id != selected_material.id for material in display_materials):
                display_materials.append(selected_material)

            detail_data["matched_base_material"] = serialize_base_material(
                selected_material,
                preferred_date=preferred_price_date,
                matched_id=selected_material.id if selected_material else None
            )

            detail_data["matched_base_materials"] = [
                serialize_base_material(
                    material,
                    preferred_date=preferred_price_date,
                    matched_id=selected_material.id if selected_material else None
                )
                for material in display_materials
            ]
        else:
            detail_data["matched_base_material"] = None
        
        # 添加分析结果
        if analysis:
            api_response = analysis.api_response or {}
            total_price_difference = api_response.get('total_price_difference')
            unit_price_difference = api_response.get('unit_price_difference')
            analysis_quantity = api_response.get('quantity') or detail_data["project_material"].get('quantity')
            analysis_unit = api_response.get('unit') or detail_data["project_material"].get('unit')
            contract_average_price = api_response.get('contract_average_price') or api_response.get('base_unit_price')
            contract_period_prices = api_response.get('contract_period_prices')

            detail_data["analysis_result"] = {
                "id": analysis.id,
                "status": analysis.status.value if hasattr(analysis.status, 'value') else str(analysis.status),
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
                "unit": analysis_unit,
                "contract_average_price": float(contract_average_price) if contract_average_price is not None else None,
                "contract_period_prices": contract_period_prices
            }
        
        # 构建分析历史记录
        analysis_history = []
        try:
            from app.models.analysis import AnalysisStatus
            
            def safe_float(value):
                try:
                    return float(value)
                except (TypeError, ValueError):
                    return None

            # 合并当前分析和历史记录
            source_iter = []
            
            # 1. 首先加入当前最新的分析记录（如果存在）
            # 只有当历史记录为空，或者当前分析记录与最新的一条历史记录不重复时才添加
            if analysis:
                is_duplicate = False
                if history_records:
                    latest_history = history_records[0]
                    # 检查是否重复：状态相同，且时间接近或模型一致
                    if analysis.status == latest_history.status:
                        # 优先比较 analyzed_at (分析完成时间)
                        check_time = analysis.analyzed_at or analysis.updated_at or analysis.created_at
                        if check_time and latest_history.created_at:
                            try:
                                time_diff = abs((check_time - latest_history.created_at).total_seconds())
                                # 如果时间差在60秒内，认为是同一条记录
                                if time_diff < 60:
                                    is_duplicate = True
                            except Exception:
                                # 如果时间比较出错，降级比较模型和价格
                                pass
                        
                        # 二次确认：如果时间比较无法确定或失败，比较关键字段
                        if not is_duplicate:
                            if (getattr(analysis, 'analysis_model', None) == getattr(latest_history, 'analysis_model', None) and
                                getattr(analysis, 'predicted_price_min', None) == getattr(latest_history, 'predicted_price_min', None) and
                                getattr(analysis, 'predicted_price_max', None) == getattr(latest_history, 'predicted_price_max', None)):
                                is_duplicate = True

                if not is_duplicate:
                    source_iter.append(analysis)
                
            # 2. 然后加入历史记录
            if history_records:
                source_iter.extend(history_records)
            
            # 如果两者都为空，尝试使用 fallback
            if not source_iter and all_analyses:
                source_iter = all_analyses
            
            for idx, hist_analysis in enumerate(source_iter):
                try:
                    status = hist_analysis.status
                    # 判断操作类型（status是枚举类型，需要比较枚举值）
                    if status == AnalysisStatus.COMPLETED:
                        action = "AI自动分析"
                        note = f"使用模型: {getattr(hist_analysis, 'analysis_model', None) or '未知'}"
                        if getattr(hist_analysis, 'analysis_cost', None):
                            note += f"，分析成本: ¥{safe_float(hist_analysis.analysis_cost):.2f}"
                        if getattr(hist_analysis, 'analysis_time', None):
                            note += f"，耗时: {safe_float(hist_analysis.analysis_time):.2f}秒"
                    elif status == AnalysisStatus.PROCESSING:
                        action = "分析进行中"
                        note = "AI正在分析中"
                    elif status == AnalysisStatus.FAILED:
                        action = "分析失败"
                        note = getattr(hist_analysis, 'analysis_reasoning', None) or "AI分析过程中出现错误"
                    else:
                        action = "分析待处理"
                        note = "等待AI分析"
                    
                    # 如果有审核记录，也添加（仅主表对象具备这些字段，历史表没有也没关系）
                    if getattr(hist_analysis, 'is_reviewed', False) and getattr(hist_analysis, 'reviewed_at', None):
                        analysis_history.append({
                            "id": f"review_{hist_analysis.id}",
                            "action": "人工审核",
                            "note": getattr(hist_analysis, 'review_notes', None) or "专家确认分析结果准确性",
                            "created_at": hist_analysis.reviewed_at.isoformat() if getattr(hist_analysis, 'reviewed_at', None) else None,
                            "created_by_name": "审核人员"  # TODO: 从reviewer关系获取用户名
                        })
                    
                    # 添加分析记录
                    analyzed_time = getattr(hist_analysis, 'analyzed_at', None) or getattr(hist_analysis, 'created_at', None)
                    if analyzed_time:
                        history_entry = {
                            "id": hist_analysis.id,
                            "action": action,
                            "note": note,
                            "created_at": analyzed_time.isoformat(),
                            "created_by_name": "AI系统",
                            "analysis_model": getattr(hist_analysis, 'analysis_model', None),
                            "predicted_price_min": safe_float(getattr(hist_analysis, 'predicted_price_min', None)),
                            "predicted_price_max": safe_float(getattr(hist_analysis, 'predicted_price_max', None)),
                            "analysis_cost": safe_float(getattr(hist_analysis, 'analysis_cost', None)),
                            "analysis_time": safe_float(getattr(hist_analysis, 'analysis_time', None)),
                            "analysis_status": status.value if hasattr(status, "value") else str(status)
                        }
                        analysis_history.append(history_entry)
                except Exception as e:
                    logger.warning(f"处理分析历史记录 {idx} 时出错: {str(e)}")
                    continue
            
            # 按时间倒序排序（最新的在前）
            analysis_history.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        except Exception as e:
            logger.error(f"构建分析历史记录失败: {str(e)}")
            analysis_history = []
        
        detail_data["analysis_history"] = analysis_history
        
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
