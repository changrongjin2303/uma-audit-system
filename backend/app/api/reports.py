from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.simple_auth import get_current_active_user, SimpleUser
from app.models.user import User
from app.services.report_service import ReportService
from app.schemas.report import (
    ReportGenerationRequest, ReportResponse, ReportListResponse,
    ReportPreviewResponse, ReportConfigSchema, BatchDeleteRequest
)
from sqlalchemy import select
from app.models.analysis import AuditReport

router = APIRouter()
report_service = ReportService()


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportGenerationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: SimpleUser = Depends(get_current_active_user)
):
    """生成审计报告"""
    try:
        return await report_service.generate_report(
            db=db,
            project_id=request.project_id,
            user_id=current_user.id,
            report_title=request.report_title,
            config=request.config,
            include_materials=request.include_materials
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成报告失败: {str(e)}")


@router.get("/", response_model=ReportListResponse)
async def get_reports(
    project_id: Optional[int] = None,
    page: int = 1,
    size: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: SimpleUser = Depends(get_current_active_user)
):
    """获取报告列表"""
    if page < 1:
        page = 1
    if size < 1 or size > 100:
        size = 10
        
    return await report_service.get_report_list(
        db=db,
        project_id=project_id,
        page=page,
        size=size
    )


@router.get("/{report_id}/preview", response_model=ReportPreviewResponse)
async def get_report_preview(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SimpleUser = Depends(get_current_active_user)
):
    """获取报告预览"""
    # 查询report_id对应的project_id
    result = await db.execute(select(AuditReport).where(AuditReport.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    return await report_service.get_report_preview(db=db, project_id=report.project_id)


@router.get("/project/{project_id}/preview", response_model=ReportPreviewResponse)
async def preview_project_report(
    project_id: int,
    include_materials: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SimpleUser = Depends(get_current_active_user)
):
    """预览项目报告数据"""
    material_ids = None
    if include_materials:
        try:
            material_ids = [int(x.strip()) for x in include_materials.split(',') if x.strip()]
        except ValueError:
            raise HTTPException(status_code=400, detail="材料ID格式错误")
    
    return await report_service.get_report_preview(
        db=db,
        project_id=project_id,
        include_materials=material_ids
    )


@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SimpleUser = Depends(get_current_active_user)
):
    """下载报告文件"""
    try:
        file_path, filename = await report_service.download_report(
            db=db,
            report_id=report_id
        )
        # 根据扩展名选择合适的媒体类型
        media_map = {
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain'
        }
        import os as _os
        from urllib.parse import quote
        ext = _os.path.splitext(filename or file_path)[1].lower()
        media_type = media_map.get(ext, 'application/octet-stream')
        
        # 手动设置Content-Disposition，避免自动添加utf-8标识
        # 使用URL编码的文件名，大多数现代浏览器都能正确识别
        encoded_filename = quote(filename)
        headers = {
            "Content-Disposition": f"attachment; filename={encoded_filename}"
        }
        
        return FileResponse(path=file_path, media_type=media_type, headers=headers)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="报告文件不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SimpleUser = Depends(get_current_active_user)
):
    """删除报告"""
    success = await report_service.delete_report(
        db=db,
        report_id=report_id,
        user_id=current_user.id
    )
    
    if success:
        return {"message": "报告删除成功"}
    else:
        raise HTTPException(status_code=500, detail="删除失败")


@router.post("/batch-delete/")
async def batch_delete_reports(
    request: BatchDeleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: SimpleUser = Depends(get_current_active_user)
):
    """批量删除报告"""
    return await report_service.batch_delete_reports(
        db=db,
        report_ids=request.report_ids,
        user_id=current_user.id
    )


@router.post("/batch-generate")
async def batch_generate_reports(
    project_ids: List[int],
    config: Optional[ReportConfigSchema] = None,
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
    current_user: SimpleUser = Depends(get_current_active_user)
):
    """批量生成报告"""
    if len(project_ids) > 10:  # 限制批量数量
        raise HTTPException(status_code=400, detail="批量生成报告数量不能超过10个")
    
    results = []
    failed_projects = []
    
    for project_id in project_ids:
        try:
            result = await report_service.generate_report(
                db=db,
                project_id=project_id,
                user_id=current_user.id,
                config=config
            )
            results.append(result)
        except Exception as e:
            failed_projects.append({
                "project_id": project_id,
                "error": str(e)
            })
    
    return {
        "success_count": len(results),
        "failed_count": len(failed_projects),
        "results": results,
        "failed_projects": failed_projects
    }


@router.get("/templates/")
async def get_report_templates(
    current_user: SimpleUser = Depends(get_current_active_user)
):
    """获取报告模板列表"""
    templates = [
        {
            "id": "default",
            "name": "标准审计报告",
            "description": "包含完整的价格分析、图表和建议措施",
            "sections": [
                "封面",
                "执行摘要", 
                "项目概况",
                "分析结果",
                "问题材料详情",
                "图表分析",
                "建议措施",
                "附录"
            ]
        },
        {
            "id": "summary",
            "name": "简化报告",
            "description": "仅包含关键统计信息和核心问题",
            "sections": [
                "执行摘要",
                "关键发现",
                "建议措施"
            ]
        },
        {
            "id": "detailed",
            "name": "详细分析报告", 
            "description": "包含每个材料的详细分析结果",
            "sections": [
                "封面",
                "执行摘要",
                "项目概况", 
                "详细分析结果",
                "材料清单",
                "价格对比表",
                "图表分析",
                "风险评估",
                "建议措施",
                "附录"
            ]
        }
    ]
    
    return {"templates": templates}


@router.get("/statistics/")
async def get_report_statistics(
    project_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SimpleUser = Depends(get_current_active_user)
):
    """获取报告统计信息"""
    from sqlalchemy import select, func
    from app.models.analysis import AuditReport
    
    # 基础查询
    query = select(func.count(AuditReport.id))
    if project_id:
        query = query.where(AuditReport.project_id == project_id)
    
    result = await db.execute(query)
    total_reports = result.scalar() or 0
    
    # 本月报告数量
    from datetime import datetime, timedelta
    this_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    month_query = select(func.count(AuditReport.id)).where(
        AuditReport.created_at >= this_month_start
    )
    if project_id:
        month_query = month_query.where(AuditReport.project_id == project_id)
    
    month_result = await db.execute(month_query)
    monthly_reports = month_result.scalar() or 0
    
    return {
        "total_reports": total_reports,
        "monthly_reports": monthly_reports,
        "average_generation_time": 15.5,  # 可以从实际数据计算
        "success_rate": 98.5  # 可以从实际数据计算
    }
