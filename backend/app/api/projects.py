from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
import json
from datetime import datetime

from app.core.database import get_db
from app.core.simple_auth import get_current_active_user, require_cost_engineer, SimpleUser
from app.models.user import User
from app.models.project import Project, ProjectMaterial
from loguru import logger
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetailResponse,
    MaterialImportRequest, MaterialImportResponse, FileUploadResponse,
    ExcelAnalysisResponse, ProjectMaterialResponse
)
from app.services.project import ProjectService, ProjectFileService
from app.utils.excel import ExcelProcessor

router = APIRouter()


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: SimpleUser = Depends(require_cost_engineer()),
    db: AsyncSession = Depends(get_db)
):
    """创建新项目"""
    project = await ProjectService.create_project(db, project_data, current_user)
    return ProjectResponse.model_validate(project)


@router.get("/")
async def get_projects(
    page: int = 1,
    size: int = 20,
    status: Optional[str] = None,
    name: Optional[str] = None,
    project_type: Optional[str] = None,
    # current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取项目列表"""
    from app.models.project import ProjectStatus
    
    # 转换分页参数
    skip = (page - 1) * size
    limit = size
    
    project_status = None
    if status:
        try:
            project_status = ProjectStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的项目状态"
            )
    
    projects = await ProjectService.get_projects(
        db, None, skip=skip, limit=limit, 
        status=project_status, search=name, project_type=project_type
    )
    
    # 获取总数
    total = await ProjectService.get_projects_count(
        db, None, status=project_status, search=name, project_type=project_type
    )
    
    # 返回分页格式
    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "items": [ProjectResponse.model_validate(project) for project in projects],
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    }


@router.get("/test-simple")
async def test_simple():
    """简单测试接口"""
    return {"message": "test simple works"}

@router.post("/test-login")
async def test_login():
    """测试登录接口（开发用）"""
    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "token": "very-long-token-for-testing-purposes-that-will-work",
            "user": {
                "id": 1,
                "username": "admin",
                "email": "admin@uma-audit.com",
                "full_name": "系统管理员",
                "role": "ADMIN",
                "department": "系统管理部",
                "is_active": True
            }
        }
    }

@router.post("/create-test-projects-dev")
async def create_test_projects_dev(
    db: AsyncSession = Depends(get_db)
):
    """创建测试项目（开发用）"""
    from app.schemas.project import ProjectCreate
    from datetime import datetime, date
    
    test_projects = [
        ProjectCreate(
            name="新测试项目",
            description="这是一个测试项目，用于验证系统功能",
            project_code="TEST001",
            location="上海市",
            owner="测试业主",
            contractor="测试承包商",
            project_type="building",
            budget_amount=1000.0,
            price_base_date=date.today()
        ),
        ProjectCreate(
            name="测试项目",
            description="另一个测试项目",
            project_code="TEST002", 
            location="北京市",
            owner="测试业主2",
            contractor="测试承包商2",
            project_type="decoration",
            budget_amount=800.0,
            price_base_date=date.today()
        )
    ]
    
    # 创建一个临时用户
    from app.core.simple_auth import SimpleUser
    temp_user = SimpleUser(user_id=1, username="admin")
    
    created_projects = []
    for project_data in test_projects:
        # 检查是否已存在相同项目代码的项目
        existing = await ProjectService.get_project_by_code(db, project_data.project_code)
        if not existing:
            project = await ProjectService.create_project(db, project_data, temp_user)
            created_projects.append(project)
    
    return {
        "message": f"成功创建 {len(created_projects)} 个测试项目",
        "projects": [{"id": p.id, "name": p.name} for p in created_projects]
    }

# 具体路由必须在通用路由前面
@router.get("/{project_id}/stats")
async def get_project_stats(
    project_id: int,
    # 开发环境暂时移除认证要求
    # # current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取项目统计信息"""
    # 验证项目存在
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 获取项目材料统计
    stats = await ProjectService.get_project_stats(db, project_id)
    
    # 获取分析结果数量
    from sqlalchemy import select, func
    from app.models.project import ProjectMaterial
    from app.models.analysis import PriceAnalysis
    
    # 查询已分析的材料数量
    stmt = select(func.count(PriceAnalysis.id)).select_from(
        ProjectMaterial.__table__.join(
            PriceAnalysis.__table__,
            ProjectMaterial.id == PriceAnalysis.material_id
        )
    ).where(
        ProjectMaterial.project_id == project_id
    )
    result = await db.execute(stmt)
    analyzed_materials = result.scalar() or 0
    
    return {
        "project_id": project_id,
        "total_materials": stats.get('total_materials', 0),
        "priced_materials": stats.get('priced_materials', 0),
        "needs_review_materials": stats.get('needs_review_materials', 0),  # 需人工复核材料
        "unpriced_materials": stats.get('unpriced_materials', 0),
        "problematic_materials": stats.get('problematic_materials', 0),
        "analyzed_materials": analyzed_materials,
        "matched_materials": stats.get('matched_materials', 0),
        "unmatched_materials": stats.get('total_materials', 0) - stats.get('matched_materials', 0) - stats.get('needs_review_materials', 0)
    }

@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: int,
    # 开发环境暂时移除认证要求
    # # current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取项目详情"""
    from loguru import logger
    logger.info(f"获取项目详情: project_id={project_id}")
    
    # 先检查项目是否存在（不考虑用户权限）
    project_exists = await ProjectService.get_project_by_id(db, project_id, None)
    if not project_exists:
        logger.warning(f"项目不存在: project_id={project_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 开发环境直接获取项目详情（跳过权限检查）
    project = await ProjectService.get_project_with_materials(
        db, project_id, None
    )
    if not project:
        logger.warning(f"项目数据获取失败: project_id={project_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="项目数据获取失败"
        )
    
    logger.info(f"成功获取项目详情: project_id={project_id}")
    return ProjectDetailResponse.model_validate(project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: SimpleUser = Depends(require_cost_engineer()),
    db: AsyncSession = Depends(get_db)
):
    """更新项目信息"""
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    updated_project = await ProjectService.update_project(db, project, project_data)
    return ProjectResponse.model_validate(updated_project)


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    current_user: SimpleUser = Depends(require_cost_engineer()),
    db: AsyncSession = Depends(get_db)
):
    """删除项目"""
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    success = await ProjectService.delete_project(db, project)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除项目失败"
        )
    
    return {"message": "项目删除成功"}


@router.post("/batch-delete")
async def batch_delete_projects(
    request: dict,
    # 开发环境暂时移除认证要求
    # current_user: SimpleUser = Depends(require_cost_engineer()),
    db: AsyncSession = Depends(get_db)
):
    """批量删除项目"""
    project_ids = request.get('ids', [])
    
    if not project_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有提供要删除的项目ID"
        )
    
    try:
        deleted_count = 0
        failed_projects = []
        
        for project_id in project_ids:
            try:
                # 开发环境下简化项目查询
                stmt = select(Project).where(Project.id == project_id)
                result = await db.execute(stmt)
                project = result.scalar_one_or_none()
                
                if project:
                    success = await ProjectService.delete_project(db, project)
                    if success:
                        deleted_count += 1
                    else:
                        failed_projects.append(project_id)
                else:
                    failed_projects.append(project_id)
            except Exception as e:
                logger.error(f"删除项目 {project_id} 失败: {e}")
                failed_projects.append(project_id)
        
        response = {
            "message": f"成功删除 {deleted_count} 个项目",
            "deleted_count": deleted_count,
            "failed_count": len(failed_projects)
        }
        
        if failed_projects:
            response["failed_projects"] = failed_projects
        
        return response
        
    except Exception as e:
        logger.error(f"批量删除项目失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="批量删除项目失败"
        )


@router.post("/{project_id}/upload-excel", response_model=FileUploadResponse)
async def upload_excel_file(
    project_id: int,
    file: UploadFile = File(...),
    # 开发环境暂时移除认证要求
    # current_user: SimpleUser = Depends(require_cost_engineer()),
    db: AsyncSession = Depends(get_db)
):
    """上传Excel文件"""
    # 验证项目存在
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    try:
        # 保存文件
        file_service = ProjectFileService()
        file_path, filename = await file_service.excel_processor.save_file(file)
        
        # 更新项目文件信息
        project.original_filename = file.filename
        project.file_path = file_path
        project.file_size = file.size
        await db.commit()
        
        # 分析Excel文件
        analysis = await file_service.analyze_excel_file(file_path)
        
        # 确保所有数值都是Python原生类型
        def convert_numpy_types(obj):
            if hasattr(obj, 'item'):  # numpy标量
                return obj.item()
            elif isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            else:
                return obj
        
        analysis = convert_numpy_types(analysis)
        
        # 如果有建议的字段映射，自动导入数据
        imported_count = 0
        if analysis.get('suggested_mapping'):
            try:
                import pandas as pd
                from app.utils.excel import ExcelProcessor
                excel_processor = ExcelProcessor()
                
                # 读取Excel文件数据
                df = excel_processor.read_excel_file(file_path)
                if df is not None and not df.empty:
                    # 根据字段映射转换数据
                    mapping = analysis['suggested_mapping']
                    materials_data = []
                    
                    for index, row in df.iterrows():
                        material_data = {
                            'material_name': str(row.get(mapping.get('material_name', ''), '')),
                            'specification': str(row.get(mapping.get('specification', ''), '')),
                            'unit': str(row.get(mapping.get('unit', ''), '')),
                            'quantity': float(row.get(mapping.get('quantity', ''), 0)) if pd.notnull(row.get(mapping.get('quantity', ''))) else 0,
                            'unit_price': float(row.get(mapping.get('unit_price', ''), 0)) if pd.notnull(row.get(mapping.get('unit_price', ''))) else 0,
                            'row_number': index + 2  # Excel行号从2开始（第1行是标题）
                        }
                        
                        # 过滤掉空的材料名称
                        if material_data['material_name'].strip():
                            materials_data.append(material_data)
                    
                    # 批量添加材料到项目
                    if materials_data:
                        materials = await ProjectService.add_materials_to_project(
                            db, project, materials_data
                        )
                        imported_count = len(materials)
                
            except Exception as import_error:
                # 导入失败不影响上传成功的响应，但要记录错误
                import logging
                logging.error(f"自动导入材料数据失败: {import_error}")
                import traceback
                logging.error(f"错误详情: {traceback.format_exc()}")
        
        return FileUploadResponse(
            message=f"文件上传成功{'，已自动导入 ' + str(imported_count) + ' 条材料数据' if imported_count > 0 else ''}",
            file_info={
                "filename": filename,
                "original_filename": file.filename,
                "size": int(file.size),
                "path": file_path
            },
            analysis=analysis
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{project_id}/analyze-excel", response_model=ExcelAnalysisResponse)
async def analyze_excel_file(
    project_id: int,
    # current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """分析已上传的Excel文件"""
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    if not project.file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="项目尚未上传Excel文件"
        )
    
    try:
        file_service = ProjectFileService()
        analysis = await file_service.analyze_excel_file(project.file_path)
        return ExcelAnalysisResponse(**analysis)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"分析Excel文件失败: {str(e)}"
        )


@router.post("/{project_id}/import-materials", response_model=MaterialImportResponse)
async def import_materials(
    project_id: int,
    import_request: MaterialImportRequest,
    # 开发环境暂时移除认证要求
    # current_user: SimpleUser = Depends(require_cost_engineer()),
    db: AsyncSession = Depends(get_db)
):
    """从Excel文件导入材料数据"""
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    if not project.file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="项目尚未上传Excel文件"
        )
    
    try:
        file_service = ProjectFileService()
        result = await file_service.process_excel_upload(
            db, project, project.file_path, import_request
        )
        
        return MaterialImportResponse(
            project_id=project_id,
            imported_count=result['imported_count'],
            skipped_count=result['skipped_count'],
            validation_result=result['validation_result'],
            materials=[
                ProjectMaterialResponse.model_validate(material) 
                for material in result['materials'][:10]  # 只返回前10条用于预览
            ]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{project_id}/materials")
async def get_project_materials(
    project_id: int,
    page: int = 1,
    size: int = 20,
    skip: int = 0,
    limit: int = 100,
    is_matched: Optional[bool] = None,
    needs_review: Optional[bool] = None,
    is_problematic: Optional[bool] = None,
    keyword: Optional[str] = Query(None, description="材料名称/编码/规格关键词"),
    unit: Optional[str] = Query(None, description="单位过滤"),
    # 开发环境暂时移除认证要求
    # # current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取项目材料列表
    
    筛选参数:
    - is_matched: 是否已匹配（相似度>=0.85）
    - needs_review: 是否需人工复核（相似度0.65-0.85）
    - is_problematic: 是否有问题
    """
    # 验证项目存在（开发环境跳过权限检查）
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 优先使用page/size参数，如果没有则使用skip/limit参数
    if page and size:
        calculated_skip = (page - 1) * size
        calculated_limit = size
    else:
        calculated_skip = skip
        calculated_limit = limit
    
    # 获取材料列表
    materials = await ProjectService.get_project_materials(
        db,
        project_id,
        skip=calculated_skip,
        limit=calculated_limit,
        is_matched=is_matched,
        needs_review=needs_review,
        is_problematic=is_problematic,
        keyword=keyword,
        unit=unit
    )
    
    # 获取总数
    from sqlalchemy import select, func, and_, or_
    from app.models.project import ProjectMaterial
    
    count_stmt = select(func.count(ProjectMaterial.id)).where(
        ProjectMaterial.project_id == project_id
    )
    
    # 应用相同的过滤条件
    if is_matched is not None:
        count_stmt = count_stmt.where(ProjectMaterial.is_matched == is_matched)
    # needs_review 字段可能不存在于旧数据库
    if needs_review is not None and hasattr(ProjectMaterial, 'needs_review'):
        try:
            count_stmt = count_stmt.where(ProjectMaterial.needs_review == needs_review)
        except Exception:
            pass  # 字段不存在，忽略
    if is_problematic is not None:
        count_stmt = count_stmt.where(ProjectMaterial.is_problematic == is_problematic)
    
    if keyword:
        keyword_str = keyword.strip()
        if keyword_str:
            keyword_pattern = f"%{keyword_str}%"
            count_stmt = count_stmt.where(
                or_(
                    ProjectMaterial.material_name.ilike(keyword_pattern),
                    ProjectMaterial.serial_number.ilike(keyword_pattern),
                    ProjectMaterial.specification.ilike(keyword_pattern)
                )
            )
    
    if unit:
        count_stmt = count_stmt.where(ProjectMaterial.unit == unit)
    
    count_result = await db.execute(count_stmt)
    total = count_result.scalar() or 0
    
    # 返回分页格式
    return {
        "items": [ProjectMaterialResponse.model_validate(material) for material in materials],
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }


@router.get("/{project_id}/materials/{material_id}", response_model=ProjectMaterialResponse)
async def get_project_material(
    project_id: int,
    material_id: int,
    # 开发环境暂时移除认证要求
    # # current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取项目单个材料详情"""
    # 验证项目存在
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 获取材料详情
    from sqlalchemy import select
    from app.models.project import ProjectMaterial
    
    stmt = select(ProjectMaterial).where(
        ProjectMaterial.id == material_id,
        ProjectMaterial.project_id == project_id
    )
    result = await db.execute(stmt)
    material = result.scalar_one_or_none()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="材料不存在"
        )
    
    return ProjectMaterialResponse.model_validate(material)


@router.post("/{project_id}/refresh-statistics")
async def refresh_project_statistics(
    project_id: int,
    current_user: SimpleUser = Depends(require_cost_engineer()),
    db: AsyncSession = Depends(get_db)
):
    """刷新项目统计信息"""
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    updated_project = await ProjectService.update_project_statistics(db, project)
    return {
        "message": "统计信息已更新",
        "statistics": {
            "total_materials": updated_project.total_materials,
            "priced_materials": updated_project.priced_materials,
            "unpriced_materials": updated_project.unpriced_materials,
            "problematic_materials": updated_project.problematic_materials
        }
    }


@router.delete("/{project_id}/materials/{material_id}")
async def delete_project_material(
    project_id: int,
    material_id: int,
    # 开发环境暂时移除认证要求
    # current_user: SimpleUser = Depends(require_cost_engineer()),
    db: AsyncSession = Depends(get_db)
):
    """删除项目材料"""
    from app.models.project import ProjectMaterial
    
    try:
        # 查找项目材料
        stmt = select(ProjectMaterial).where(
            ProjectMaterial.id == material_id,
            ProjectMaterial.project_id == project_id
        )
        result = await db.execute(stmt)
        material = result.scalar_one_or_none()
        
        if not material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目材料不存在"
            )
        
        # 删除材料
        await db.delete(material)
        await db.commit()
        
        return {"message": "项目材料删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除项目材料失败: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除项目材料失败"
        )


@router.post("/{project_id}/materials/{material_id}/cancel-match")
async def cancel_project_material_match(
    project_id: int,
    material_id: int,
    db: AsyncSession = Depends(get_db),
    # TODO: 生产环境需要恢复认证
    # current_user: SimpleUser = Depends(get_current_active_user)
):
    """取消项目材料匹配"""
    try:
        # 验证项目是否存在
        project_stmt = select(Project).where(Project.id == project_id)
        project_result = await db.execute(project_stmt)
        project = project_result.scalar_one_or_none()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        # 查找项目材料
        stmt = select(ProjectMaterial).where(
            ProjectMaterial.project_id == project_id,
            ProjectMaterial.id == material_id,
        )
        result = await db.execute(stmt)
        material = result.scalar_one_or_none()
        
        if not material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目材料不存在"
            )
        
        # 取消匹配
        material.is_matched = False
        material.matched_material_id = None
        material.match_score = None
        material.match_method = None
        material.updated_at = datetime.utcnow()
        
        await db.commit()
        
        return {"message": "已取消材料匹配"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取消材料匹配失败: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="取消材料匹配失败"
        )


@router.put("/{project_id}/materials/{material_id}")
async def update_project_material(
    project_id: int,
    material_id: int,
    update_data: dict,
    db: AsyncSession = Depends(get_db),
    # TODO: 生产环境需要恢复认证
    # current_user: SimpleUser = Depends(get_current_active_user)
):
    """更新项目材料信息"""
    try:
        # 验证项目是否存在
        project_stmt = select(Project).where(Project.id == project_id)
        project_result = await db.execute(project_stmt)
        project = project_result.scalar_one_or_none()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        # 查找项目材料
        stmt = select(ProjectMaterial).where(
            ProjectMaterial.project_id == project_id,
            ProjectMaterial.id == material_id,
        )
        result = await db.execute(stmt)
        material = result.scalar_one_or_none()
        
        if not material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目材料不存在"
            )
        
        # 验证必填字段
        if 'material_name' in update_data and not update_data['material_name']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="材料名称不能为空"
            )
        
        if 'unit' in update_data and not update_data['unit']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="计量单位不能为空"
            )
        
        if 'quantity' in update_data and update_data['quantity'] <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="数量必须大于0"
            )
        
        if 'unit_price' in update_data and update_data['unit_price'] <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="单价必须大于0"
            )
        
        # 更新材料信息
        for field, value in update_data.items():
            if hasattr(material, field):
                setattr(material, field, value)
        
        # 重新计算总价
        if 'quantity' in update_data or 'unit_price' in update_data:
            material.total_price = material.quantity * material.unit_price
        
        material.updated_at = datetime.utcnow()
        
        await db.commit()
        
        return {"message": "材料信息更新成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新材料信息失败: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新材料信息失败"
        )


@router.post("/{project_id}/parse-material-excel")
async def parse_project_material_excel(
    project_id: int,
    file: UploadFile = File(...),
    sheet_name: Optional[str] = Form(None),
    # TODO: 生产环境需要恢复认证
    # current_user: SimpleUser = Depends(get_current_active_user)
):
    """解析项目材料Excel文件结构 - 使用与基础材料相同的逻辑"""
    try:
        # 验证文件类型
        allowed_types = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                        'application/vnd.ms-excel', 'text/csv']
        if file.content_type not in allowed_types and not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的文件格式，请上传Excel或CSV文件"
            )
        
        # 验证文件大小 (50MB)
        content = await file.read()
        if len(content) > 50 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件大小不能超过50MB"
            )
        
        # 解析文件结构 - 使用与基础材料完全相同的逻辑
        excel_processor = ExcelProcessor()
        
        # 重置文件指针
        import io
        file_like = io.BytesIO(content)
        
        # 分析文件结构，传递指定的工作表名称
        analysis_result = excel_processor.analyze_file_structure(file_like, file.filename, sheet_name=sheet_name)
        
        # 清理不能JSON序列化的值
        def clean_for_json(obj):
            import numpy as np
            import pandas as pd
            if isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_json(item) for item in obj]
            elif isinstance(obj, (np.integer, int)):
                return int(obj)
            elif isinstance(obj, (np.floating, float)):
                if np.isnan(obj) or np.isinf(obj):
                    return None
                return float(obj)
            elif pd.isna(obj):
                return None
            else:
                return obj
        
        cleaned_result = clean_for_json(analysis_result)
        
        return {
            "code": 200,
            "message": "文件解析成功",
            "data": cleaned_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Excel文件解析失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件解析失败: {str(e)}"
        )


@router.post("/{project_id}/get-preview-data")
async def get_project_material_preview_data(
    project_id: int,
    file: UploadFile = File(...),
    sheet_name: Optional[str] = Form(None),
    max_rows: Optional[int] = Form(2000),
    # TODO: 生产环境需要恢复认证
    # current_user: SimpleUser = Depends(get_current_active_user)
):
    """获取项目材料Excel文件预览数据用于导入"""
    try:
        # 验证文件类型
        allowed_types = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                        'application/vnd.ms-excel', 'text/csv']
        if file.content_type not in allowed_types and not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的文件格式，请上传Excel或CSV文件"
            )
        
        # 验证文件大小 (50MB)
        content = await file.read()
        if len(content) > 50 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件大小不能超过50MB"
            )
        
        # 获取预览数据
        excel_processor = ExcelProcessor()
        
        # 重置文件指针
        import io
        file_like = io.BytesIO(content)
        
        # 获取完整数据用于导入
        import_result = excel_processor.get_full_data_for_import(
            file_like, file.filename, sheet_name=sheet_name, max_preview_rows=100  # 预览只显示100行
        )
        
        # 清理不能JSON序列化的值
        def clean_for_json(obj):
            import numpy as np
            import pandas as pd
            if isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_json(item) for item in obj]
            elif isinstance(obj, (np.integer, int)):
                return int(obj)
            elif isinstance(obj, (np.floating, float)):
                if np.isnan(obj) or np.isinf(obj):
                    return None
                return float(obj)
            elif pd.isna(obj):
                return None
            else:
                return obj
        
        cleaned_result = clean_for_json(import_result)
        
        return {
            "code": 200,
            "message": f"数据获取成功，共{cleaned_result['totalRows']}行数据，预览{cleaned_result['previewRows']}行",
            "data": cleaned_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取项目材料预览数据失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取预览数据失败: {str(e)}"
        )


@router.post("/{project_id}/add-materials")
async def add_project_materials(
    project_id: int,
    materials_data: Dict[str, Any],
    # TODO: 生产环境需要恢复认证
    # # current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """直接添加项目材料数据"""
    try:
        # 验证项目存在
        project = await ProjectService.get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        materials = materials_data.get('materials', [])
        
        # 处理双重嵌套的情况
        if isinstance(materials, dict) and 'materials' in materials:
            logger.info("检测到双重嵌套结构，正在解包...")
            materials = materials['materials']
        
        if not materials:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有提供材料数据"
            )
        
        logger.info(f"准备导入 {len(materials)} 条项目材料数据")
        
        success_count = 0
        failed_count = 0
        errors = []
        
        for material_data in materials:
            try:
                # 创建项目材料记录
                from app.models.project import ProjectMaterial
                
                project_material = ProjectMaterial(
                    project_id=project_id,
                    material_name=material_data.get('name', ''),  # 前端发送的是 'name' 不是 'material_name'
                    specification=material_data.get('specification', ''),
                    unit=material_data.get('unit', ''),
                    quantity=float(material_data.get('quantity', 0)),
                    unit_price=float(material_data.get('unit_price', 0)),
                    total_price=float(material_data.get('quantity', 0)) * float(material_data.get('unit_price', 0)),  # 计算总价
                    notes=material_data.get('remarks', ''),  # 前端发送的是 'remarks' 不是 'notes'
                    row_number=material_data.get('row_number', 0),
                    is_analyzed=False,  # 默认未分析
                    is_problematic=False  # 默认无问题
                )
                
                db.add(project_material)
                success_count += 1
                
            except Exception as e:
                failed_count += 1
                errors.append(f"第{material_data.get('row_number', '未知')}行: {str(e)}")
        
        # 提交数据库事务
        await db.commit()
        
        return {
            "code": 200,
            "message": "材料添加完成",
            "data": {
                "success_count": success_count,
                "failed_count": failed_count,
                "total_count": len(materials),
                "errors": errors
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"添加项目材料失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加材料失败: {str(e)}"
        )


@router.get("/{project_id}/export")
async def export_project_data(
    project_id: int,
    format: str = "excel",
    # 开发环境暂时移除认证要求
    # # current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """导出项目数据"""
    from fastapi.responses import FileResponse
    from app.services.batch_export_service import BatchExportService
    
    # 验证项目存在
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    try:
        batch_export_service = BatchExportService()
        
        if format.lower() == "comprehensive":
            # 导出综合包
            export_path = await batch_export_service.export_project_comprehensive_package(
                db=db,
                project_id=project_id,
                user_id=1,  # 开发环境使用固定用户ID
                include_raw_data=True,
                include_analysis_results=True,
                include_attachments=True
            )
        else:
            # 导出单个项目报告
            export_path = await batch_export_service.batch_export_reports(
                db=db,
                project_ids=[project_id],
                user_id=1,  # 开发环境使用固定用户ID
                export_format="zip"
            )
        
        # 返回文件下载
        import os
        filename = os.path.basename(export_path)
        
        return FileResponse(
            path=export_path,
            filename=filename,
            media_type='application/zip'
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出失败: {str(e)}"
        )


@router.post("/{project_id}/get-preview-data")
async def get_project_material_preview_data(
    project_id: int,
    file: UploadFile = File(...),
    data: str = Form(...),
    # current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取项目材料Excel文件预览数据用于导入"""
    try:
        # 验证项目存在
        project_stmt = select(Project).where(Project.id == project_id)
        project_result = await db.execute(project_stmt)
        project = project_result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        # 验证文件类型
        allowed_types = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                        'application/vnd.ms-excel', 'text/csv']
        if file.content_type not in allowed_types and not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的文件格式，请上传Excel或CSV文件"
            )
        
        # 验证文件大小 (50MB)
        content = await file.read()
        if len(content) > 50 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件大小不能超过50MB"
            )
        
        # 解析请求数据
        try:
            import json
            request_data = json.loads(data)
            column_mapping = request_data.get('column_mapping', {})
            data_options = request_data.get('data_options', {})
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请求数据格式错误"
            )
        
        # 获取预览数据
        excel_processor = ExcelProcessor()
        
        # 重置文件指针
        import io
        file_stream = io.BytesIO(content)
        
        logger.info(f"开始处理数据: 总行数=获取中, 预览行数=获取中")
        
        # 使用get_full_data_for_import方法获取完整数据
        result_data = excel_processor.get_full_data_for_import(
            file_stream=file_stream,
            filename=file.filename,
            column_mapping=column_mapping,
            sheet_name=data_options.get('sheet_name'),
            start_row=data_options.get('start_row', 2),
            has_header=data_options.get('has_header', True),
            max_rows=None  # 获取全部数据
        )
        
        # 构造材料数据，确保符合项目材料的字段结构
        materials_data = []
        if 'materials' in result_data:
            for item in result_data['materials']:
                material_item = {
                    'material_name': item.get('name') or item.get('material_name', ''),
                    'specification': item.get('specification', ''),
                    'unit': item.get('unit', ''),
                    'quantity': float(item.get('quantity', 0)) if item.get('quantity') else 0,
                    'unit_price': float(item.get('unit_price') or item.get('price', 0)) if item.get('unit_price') or item.get('price') else 0,
                    'total_price': float(item.get('total_price', 0)) if item.get('total_price') else 0,
                    'notes': item.get('notes') or item.get('remarks', ''),
                    'row_number': item.get('row_number', 0)
                }
                materials_data.append(material_item)
        
        # 返回处理后的数据
        response_data = {
            'materials': materials_data,
            'total_count': len(materials_data),
            'preview_count': min(100, len(materials_data)),  # 预览限制100条
            'column_info': result_data.get('column_info', []),
            'file_info': {
                'filename': file.filename,
                'size': len(content),
                'rows': len(materials_data)
            }
        }
        
        logger.info(f"数据获取完成: 总行数{len(materials_data)}, 完整数据{len(materials_data)}, 预览行数{min(100, len(materials_data))}, 表头行1")
        
        return {
            'code': 200,
            'message': '数据获取成功',
            'data': response_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取预览数据失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取预览数据失败: {str(e)}"
        )


@router.post("/{project_id}/materials/batch-delete")
async def batch_delete_project_materials(
    project_id: int,
    material_ids: List[int],
    # 开发环境暂时移除认证要求
    # # current_user: SimpleUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """批量删除项目材料"""
    try:
        # 验证项目存在
        project = await ProjectService.get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        # 批量删除材料 - 直接在API中实现
        from sqlalchemy import select, and_
        from app.models.project import ProjectMaterial
        
        stmt = select(ProjectMaterial).where(
            and_(
                ProjectMaterial.project_id == project_id,
                ProjectMaterial.id.in_(material_ids)
            )
        )
        result = await db.execute(stmt)
        materials_to_delete = result.scalars().all()
        
        # 执行删除
        deleted_count = 0
        for material in materials_to_delete:
            await db.delete(material)
            deleted_count += 1
        
        await db.commit()
        logger.info(f"批量删除项目材料成功: 项目ID={project_id}, 删除数量={deleted_count}")
        
        return {
            "code": 200,
            "message": f"成功删除 {deleted_count} 个材料",
            "data": {
                "deleted_count": deleted_count,
                "material_ids": material_ids
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量删除项目材料失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量删除材料失败: {str(e)}"
        )