import os
import asyncio
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from fastapi import HTTPException
from loguru import logger

from app.models.project import Project, ProjectMaterial
from app.models.analysis import PriceAnalysis, AuditReport
from app.models.user import User
from app.schemas.report import (
    ReportConfigSchema, ReportResponse, ReportStatistics, 
    ReportListResponse, ChartDataResponse, ReportPreviewResponse,
    ReportType, ReportStatus
)
from app.services.report_generator import ReportGenerator
from app.core.config import settings


class ReportService:
    """报告服务"""
    
    def __init__(self):
        self.generator = ReportGenerator()
        
    async def generate_report(
        self,
        db: AsyncSession,
        project_id: int,
        user_id: int,
        report_title: Optional[str] = None,
        config: Optional[ReportConfigSchema] = None,
        include_materials: Optional[List[int]] = None,
        chart_images: Optional[Dict[str, str]] = None
    ) -> ReportResponse:
        """生成审计报告"""
        try:
            # 获取项目信息
            project = await self._get_project(db, project_id)
            if not project:
                raise HTTPException(status_code=404, detail="项目不存在")
            
            # 获取项目材料
            materials = await self._get_project_materials(db, project_id, include_materials)
            
            # 如果没有材料数据，创建示例数据用于测试
            if not materials:
                materials = self._create_sample_materials(project_id)
                logger.info(f"项目{project_id}没有材料数据，使用示例数据生成报告")
            
            # 获取价格分析结果
            analyses = await self._get_price_analyses(db, [m.id for m in materials])
            
            # 如果没有分析结果，创建示例分析数据
            if not analyses:
                analyses = self._create_sample_analyses(materials)
                logger.info(f"项目{project_id}没有分析数据，使用示例数据生成报告")
            
            # 使用默认配置
            if not config:
                config = ReportConfigSchema()
            
            # 生成报告标题
            if not report_title:
                report_title = f"{project.name} - 造价材料审计报告"
            
            # 创建报告记录
            audit_report = AuditReport(
                project_id=project_id,
                report_title=report_title,
                report_type=config.report_type.value,
                total_materials_count=len(materials),
                problematic_materials_count=len([m for m in materials if m.is_problematic]),
                generated_by=user_id,
                is_final=False
            )
            
            db.add(audit_report)
            await db.commit()
            await db.refresh(audit_report)
            
            # 生成报告文件
            try:
                # 调用异步生成器
                report_path = await self.generator.generate_audit_report(
                    db,
                    project,
                    materials,
                    analyses,
                    config.dict() if config else {},
                    chart_images=chart_images
                )
                
                # 更新报告记录
                audit_report.report_file_path = report_path
                try:
                    from pathlib import Path as _Path
                    audit_report.report_filename = _Path(report_path).name
                except Exception:
                    # 兜底，不影响主流程
                    audit_report.report_filename = None
                audit_report.file_size = os.path.getsize(report_path) if os.path.exists(report_path) else 0
                audit_report.generation_time = 0  # 这里可以记录实际生成时间
                
                # 计算统计信息
                stats = self._calculate_statistics(materials, analyses)
                audit_report.total_price_variance = stats['avg_price_variance']
                audit_report.estimated_savings = stats['estimated_savings']
                # 与统计对齐
                audit_report.total_materials_count = stats['total_materials']
                audit_report.problematic_materials_count = stats['problematic_materials']
                audit_report.key_findings = {
                    "analysis_coverage": stats['analysis_coverage'],
                    "problem_rate": stats['problem_rate'],
                    "risk_distribution": stats['risk_distribution']
                }
                
                await db.commit()
                await db.refresh(audit_report)
                
                logger.info(f"报告生成成功: 项目{project_id}, 报告ID{audit_report.id}")
                
            except Exception as e:
                logger.error(f"报告生成失败: {e}")
                # 标记报告生成失败
                audit_report.report_filename = "生成失败"
                await db.commit()
                raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}")
            
            return ReportResponse(
                report_id=audit_report.id,
                project_id=project_id,
                report_title=report_title,
                project_name=project.name,
                report_type=ReportType(config.report_type),
                status=ReportStatus.COMPLETED,
                file_path=audit_report.report_file_path,
                file_size=audit_report.file_size,
                generation_time=audit_report.generation_time,
                created_at=audit_report.created_at,
                download_url=f"/api/v1/reports/{audit_report.id}/download"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"生成报告时发生错误: {e}")
            raise HTTPException(status_code=500, detail="生成报告失败")
    
    async def get_report_list(
        self,
        db: AsyncSession,
        project_id: Optional[int] = None,
        page: int = 1,
        size: int = 10
    ) -> ReportListResponse:
        """获取报告列表"""
        try:
            # 构建查询
            query = select(AuditReport).order_by(desc(AuditReport.created_at))
            
            if project_id:
                query = query.where(AuditReport.project_id == project_id)
            
            # 分页
            offset = (page - 1) * size
            reports_query = query.offset(offset).limit(size)
            
            result = await db.execute(reports_query)
            reports = result.scalars().all()
            
            # 获取总数
            count_query = select(AuditReport)
            if project_id:
                count_query = count_query.where(AuditReport.project_id == project_id)
            
            count_result = await db.execute(count_query)
            total = len(count_result.scalars().all())
            
            # 转换为响应格式
            # 查询项目名称，避免逐条查询
            project_ids = {report.project_id for report in reports if report.project_id is not None}
            project_names: Dict[int, str] = {}
            if project_ids:
                project_query = select(Project.id, Project.name).where(Project.id.in_(project_ids))
                project_rows = await db.execute(project_query)
                project_names = {row.id: row.name for row in project_rows.all() if row.name}

            def build_display_title(raw_title: Optional[str], project_name: Optional[str], project_id: Optional[int]) -> str:
                base_title = (raw_title or '').strip()

                if project_id is not None:
                    pattern_with_dash = rf'^(?:项目\s*)?{project_id}\s*[-–—]\s*'
                    base_title = re.sub(pattern_with_dash, '', base_title, flags=re.IGNORECASE)
                    pattern_plain = rf'^(?:项目\s*)?{project_id}\b'
                    base_title = re.sub(pattern_plain, '', base_title, flags=re.IGNORECASE).lstrip('-–— ').strip()

                if not base_title:
                    base_title = '分析报告'

                if project_name:
                    normalized_title = base_title.lower()
                    normalized_project = project_name.lower()
                    if normalized_project not in normalized_title:
                        return f"{project_name} - {base_title}"

                return base_title

            report_responses = []
            for report in reports:
                status = ReportStatus.COMPLETED if report.report_file_path else ReportStatus.FAILED
                project_name = project_names.get(report.project_id)
                display_title = build_display_title(report.report_title, project_name, report.project_id)

                report_responses.append(ReportResponse(
                    report_id=report.id,
                    project_id=report.project_id,
                    report_title=display_title,
                    project_name=project_name,
                    report_type=ReportType(report.report_type),
                    status=status,
                    file_path=report.report_file_path,
                    file_size=report.file_size,
                    generation_time=report.generation_time,
                    created_at=report.created_at,
                    download_url=f"/api/v1/reports/{report.id}/download" if report.report_file_path else None
                ))
            
            return ReportListResponse(
                reports=report_responses,
                total=total,
                page=page,
                size=size
            )
            
        except Exception as e:
            logger.error(f"获取报告列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取报告列表失败")
    
    async def get_report_preview(
        self,
        db: AsyncSession,
        project_id: int,
        include_materials: Optional[List[int]] = None
    ) -> ReportPreviewResponse:
        """获取报告预览数据"""
        try:
            # 获取项目信息
            project = await self._get_project(db, project_id)
            if not project:
                raise HTTPException(status_code=404, detail="项目不存在")
            
            # 获取材料和分析数据
            materials = await self._get_project_materials(db, project_id, include_materials)
            if not materials:
                # 为空时提供示例材料，保证预览有可视内容
                materials = self._create_sample_materials(project_id)
            analyses = await self._get_price_analyses(db, [m.id for m in materials])
            if not analyses:
                analyses = self._create_sample_analyses(materials)
            
            # 计算统计信息
            stats = self._calculate_statistics(materials, analyses)
            
            # 生成图表数据
            chart_data = self._generate_chart_data(materials, analyses)
            
            # 获取样本问题材料
            problematic_materials = [m for m in materials if m.is_problematic][:5]  # 只取前5个
            sample_materials = []
            
            for material in problematic_materials:
                sample_materials.append({
                    "id": material.id,
                    "name": material.material_name,
                    "specification": material.specification,
                    "unit_price": material.unit_price,
                    "issue": self._get_material_issue(material, analyses)
                })
            
            # 生成完整的分析材料数据
            analysis_materials = self._generate_analysis_materials_data(materials, analyses)
            
            # 筛选核增（减）额为正数的数据，并按权重百分比降序排序，显示全部数据
            analysis_materials = [
                m for m in analysis_materials 
                if m.get('adjustment', 0) > 0
            ]
            # 使用权重百分比进行排序，权重高的材料排在前面
            analysis_materials.sort(
                key=lambda x: x.get('weight_percentage', 0),
                reverse=True
            )
            
            # 生成市场信息价材料数据
            guidance_price_materials = await self._generate_guidance_price_materials_data(db, project_id, materials, analyses)
            
            return ReportPreviewResponse(
                project_name=project.name,
                statistics=ReportStatistics(**stats),
                chart_data=chart_data,
                sample_problematic_materials=sample_materials,
                analysis_materials=analysis_materials,
                guidance_price_materials=guidance_price_materials
            )
            
        except Exception as e:
            logger.error(f"获取报告预览失败: {e}")
            raise HTTPException(status_code=500, detail="获取报告预览失败")
    
    async def download_report(
        self,
        db: AsyncSession,
        report_id: int
    ) -> tuple[str, str]:
        """下载报告文件
        
        Returns:
            (file_path, filename)
        """
        try:
            # 获取报告记录
            query = select(AuditReport).where(AuditReport.id == report_id)
            result = await db.execute(query)
            report = result.scalar_one_or_none()
            
            if not report:
                raise HTTPException(status_code=404, detail="报告不存在")
            
            if not report.report_file_path or not os.path.exists(report.report_file_path):
                raise HTTPException(status_code=404, detail="报告文件不存在")
            
            filename = report.report_filename or f"分析报告_{report.id}.docx"
            return report.report_file_path, filename
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"下载报告失败: {e}")
            raise HTTPException(status_code=500, detail="下载报告失败")
    
    async def delete_report(
        self,
        db: AsyncSession,
        report_id: int,
        user_id: int
    ) -> bool:
        """删除报告"""
        try:
            # 获取报告记录
            query = select(AuditReport).where(AuditReport.id == report_id)
            result = await db.execute(query)
            report = result.scalar_one_or_none()
            
            if not report:
                raise HTTPException(status_code=404, detail="报告不存在")
            
            # 删除文件
            if report.report_file_path and os.path.exists(report.report_file_path):
                try:
                    os.remove(report.report_file_path)
                except Exception as e:
                    logger.warning(f"删除报告文件失败: {e}")
            
            # 删除数据库记录
            await db.delete(report)
            await db.commit()
            
            logger.info(f"报告删除成功: ID{report_id}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"删除报告失败: {e}")
            raise HTTPException(status_code=500, detail="删除报告失败")

    async def batch_delete_reports(
        self,
        db: AsyncSession,
        report_ids: List[int],
        user_id: int
    ) -> Dict[str, Any]:
        """批量删除报告"""
        try:
            # 获取所有要删除的报告
            query = select(AuditReport).where(AuditReport.id.in_(report_ids))
            result = await db.execute(query)
            reports = result.scalars().all()
            
            if not reports:
                return {"success": True, "count": 0}
            
            deleted_count = 0
            for report in reports:
                # 删除文件
                if report.report_file_path and os.path.exists(report.report_file_path):
                    try:
                        os.remove(report.report_file_path)
                    except Exception as e:
                        logger.warning(f"删除报告文件失败: {e}")
                
                # 删除数据库记录
                await db.delete(report)
                deleted_count += 1
            
            await db.commit()
            
            logger.info(f"批量删除报告成功: {deleted_count}个")
            return {
                "success": True, 
                "count": deleted_count,
                "requested_count": len(report_ids)
            }
            
        except Exception as e:
            logger.error(f"批量删除报告失败: {e}")
            raise HTTPException(status_code=500, detail=f"批量删除报告失败: {str(e)}")
    
    async def _get_project(self, db: AsyncSession, project_id: int) -> Optional[Project]:
        """获取项目信息"""
        query = select(Project).where(Project.id == project_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def _get_project_materials(
        self,
        db: AsyncSession,
        project_id: int,
        include_materials: Optional[List[int]] = None
    ) -> List[ProjectMaterial]:
        """获取项目材料"""
        query = select(ProjectMaterial).where(ProjectMaterial.project_id == project_id)
        
        if include_materials:
            query = query.where(ProjectMaterial.id.in_(include_materials))
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def _get_price_analyses(
        self,
        db: AsyncSession,
        material_ids: List[int]
    ) -> List[PriceAnalysis]:
        """获取价格分析结果"""
        if not material_ids:
            return []
        
        query = select(PriceAnalysis).where(PriceAnalysis.material_id.in_(material_ids))
        result = await db.execute(query)
        return result.scalars().all()
    
    def _calculate_statistics(
        self,
        materials: List[ProjectMaterial],
        analyses: List[PriceAnalysis]
    ) -> Dict[str, Any]:
        """计算统计信息
        - 分析数量按 PriceAnalysis 记录统计（而不是仅依赖 ProjectMaterial.is_analyzed）
        - 风险等级若缺失，按价格偏差进行推断
        """
        total_materials = len(materials)

        # 分析覆盖：以实际存在的分析记录为准，兼容材料标记
        analyzed_ids_from_flag = {m.id for m in materials if getattr(m, 'is_analyzed', False)}
        analyzed_ids_from_analysis = {a.material_id for a in analyses if a is not None}
        analyzed_set = analyzed_ids_from_flag | analyzed_ids_from_analysis
        analyzed_materials = len(analyzed_set)

        # 问题材料：材料标记 + 分析判断不合理
        price_analyses_dict = {a.material_id: a for a in analyses}
        problematic_from_material = {m.id for m in materials if getattr(m, 'is_problematic', False)}
        problematic_from_analysis = {a.material_id for a in analyses if a.is_reasonable is False}
        problematic_set = problematic_from_material | problematic_from_analysis
        problematic_materials = len(problematic_set)

        # 不合理数量
        unreasonable_count = len(problematic_from_analysis)

        # 风险等级统计（缺失时按偏差推断）
        def infer_risk_level(a: PriceAnalysis) -> str:
            if a is None:
                return 'unknown'
            if a.risk_level:
                return a.risk_level
            try:
                v = abs(a.price_variance or 0)
                if v >= 60:
                    return 'severe'
                if v >= 40:
                    return 'high'
                if v >= 20:
                    return 'medium'
                return 'low'
            except Exception:
                return 'unknown'

        risk_stats: Dict[str, int] = {}
        for a in analyses:
            level = infer_risk_level(a)
            risk_stats[level] = risk_stats.get(level, 0) + 1

        # 价格偏差
        price_variances = [a.price_variance for a in analyses if a and a.price_variance is not None]
        avg_variance = sum(price_variances) / len(price_variances) if price_variances else 0

        # 估算节约金额（仅高于预测均价的材料计入）
        estimated_savings = 0
        for m in materials:
            a = price_analyses_dict.get(m.id)
            if a and a.predicted_price_avg and m.unit_price:
                if m.unit_price > a.predicted_price_avg:
                    estimated_savings += (m.unit_price - a.predicted_price_avg) * (m.quantity or 0)

        analysis_coverage = (analyzed_materials / total_materials * 100) if total_materials > 0 else 0
        problem_rate = (problematic_materials / total_materials * 100) if total_materials > 0 else 0

        return {
            'total_materials': total_materials,
            'analyzed_materials': analyzed_materials,
            'problematic_materials': problematic_materials,
            'unreasonable_count': unreasonable_count,
            'analysis_coverage': analysis_coverage,
            'problem_rate': problem_rate,
            'avg_price_variance': avg_variance,
            'estimated_savings': estimated_savings,
            'risk_distribution': risk_stats
        }
    
    def _generate_chart_data(
        self,
        materials: List[ProjectMaterial],
        analyses: List[PriceAnalysis]
    ) -> List[ChartDataResponse]:
        """生成图表数据"""
        chart_data = []
        
        # 风险等级分布饼图数据（缺失时按偏差推断）
        def infer_level(a: PriceAnalysis) -> str:
            if not a:
                return 'unknown'
            if a.risk_level:
                return a.risk_level
            try:
                v = abs(a.price_variance or 0)
                if v >= 60:
                    return 'severe'
                if v >= 40:
                    return 'high'
                if v >= 20:
                    return 'medium'
                return 'low'
            except Exception:
                return 'unknown'
        risk_stats = {}
        for a in analyses:
            level = infer_level(a)
            risk_stats[level] = risk_stats.get(level, 0) + 1
        
        if risk_stats:
            chart_data.append(ChartDataResponse(
                chart_type="risk_levels",
                data={
                    "labels": list(risk_stats.keys()),
                    "values": list(risk_stats.values())
                }
            ))
        
        # 价格分布直方图数据
        prices = [a.predicted_price_avg for a in analyses if a.predicted_price_avg]
        if prices:
            chart_data.append(ChartDataResponse(
                chart_type="price_distribution",
                data={
                    "prices": prices,
                    "bins": 20
                }
            ))
        
        # 价格偏差条形图数据
        variances = []
        material_names = []
        for i, analysis in enumerate(analyses[:20]):  # 只取前20个
            if analysis.price_variance is not None:
                variances.append(analysis.price_variance)
                material_names.append(f"材料{i+1}")
        
        if variances:
            chart_data.append(ChartDataResponse(
                chart_type="price_variance",
                data={
                    "materials": material_names,
                    "variances": variances
                }
            ))
        
        return chart_data
    
    def _get_material_issue(
        self,
        material: ProjectMaterial,
        analyses: List[PriceAnalysis]
    ) -> str:
        """获取材料问题描述"""
        analysis = next((a for a in analyses if a.material_id == material.id), None)
        
        if not analysis:
            return "缺少价格分析"
        
        issues = []
        if analysis.is_reasonable == False:
            issues.append("价格不合理")
        
        if analysis.price_variance and abs(analysis.price_variance) > 30:
            issues.append(f"价格偏差{analysis.price_variance:.1f}%")
        
        if analysis.risk_level in ['high', 'severe']:
            issues.append(f"风险等级：{analysis.risk_level}")
        
        return '；'.join(issues) if issues else "需要人工确认"
    
    def _create_sample_materials(self, project_id: int) -> List[ProjectMaterial]:
        """创建示例材料数据"""
        # 使用报告生成器中的方法
        return self.generator._create_sample_materials(project_id)
    
    def _create_sample_analyses(self, materials: List[ProjectMaterial]) -> List[PriceAnalysis]:
        """创建示例分析数据"""
        # 使用报告生成器中的方法
        return self.generator._create_sample_analyses(materials)
    
    def _generate_analysis_materials_data(
        self,
        materials: List[ProjectMaterial],
        analyses: List[PriceAnalysis]
    ) -> List[Dict[str, Any]]:
        """生成分析材料数据，用于前端表格展示"""
        result = []
        
        for material in materials:
            # 找到对应的价格分析
            analysis = next((a for a in analyses if a.material_id == material.id), None)
            
            # 计算相关价格数据
            original_price = material.unit_price or 0
            quantity = material.quantity or 1
            
            if analysis:
                ai_price = analysis.predicted_price_avg or 0
                ai_price_min = analysis.predicted_price_min or ai_price * 0.9
                ai_price_max = analysis.predicted_price_max or ai_price * 1.1
                # 使用预测价格区间的中值作为AI推荐价格
                ai_recommended_price = (ai_price_min + ai_price_max) / 2 if ai_price_min and ai_price_max else ai_price
            else:
                # 没有分析数据时，使用原价格的90%作为AI推荐价格（示例）
                ai_recommended_price = original_price * 0.9
            
            # 计算合计价格和调整额
            original_total = original_price * quantity
            ai_total = ai_recommended_price * quantity
            adjustment = original_total - ai_total
            
            # 计算权重百分比（基于合计金额占比）
            total_amount = sum((m.unit_price or 0) * (m.quantity or 1) for m in materials)
            weight_percentage = (original_total / total_amount * 100) if total_amount > 0 else 0
            
            material_data = {
                "id": material.id,
                "material_name": material.material_name,
                "specification": material.specification or "",
                "unit": material.unit or "个",
                "quantity": quantity,
                "original_price": original_price,
                "ai_predicted_price": ai_recommended_price,
                "predicted_price": ai_recommended_price,  # 兼容字段
                "original_total_price": original_total,
                "ai_total_price": ai_total,
                "adjustment": adjustment,
                "weight_percentage": weight_percentage,
                "risk_level": analysis.risk_level if analysis else "medium",
                "is_reasonable": analysis.is_reasonable if analysis else None,
                "analysis_date": analysis.analyzed_at.isoformat() if analysis and analysis.analyzed_at else None
            }
            
            result.append(material_data)
        
        # 按权重降序排列
        result.sort(key=lambda x: x["weight_percentage"], reverse=True)
        
        return result
    
    async def _generate_guidance_price_materials_data(
        self,
        db: AsyncSession,
        project_id: int,
        materials: List[ProjectMaterial],
        analyses: List[PriceAnalysis]
    ) -> List[Dict[str, Any]]:
        """生成市场信息价材料数据，用于前端表格展示"""
        result = []
        
        try:
            # 从数据库获取实际的市场信息价材料分析数据
            from app.models.analysis import PriceAnalysis as PriceAnalysisModel
            from sqlalchemy import select, and_, func
            
            # 查询市场信息价材料分析结果
            stmt = select(
                PriceAnalysisModel.material_id,
                PriceAnalysisModel.api_response,
                PriceAnalysisModel.created_at,
                ProjectMaterial.material_name,
                ProjectMaterial.specification,
                ProjectMaterial.unit,
                ProjectMaterial.quantity,
                ProjectMaterial.unit_price
            ).select_from(
                PriceAnalysisModel.__table__.join(
                    ProjectMaterial, PriceAnalysisModel.material_id == ProjectMaterial.id
                )
            ).where(
                and_(
                    ProjectMaterial.project_id == project_id,
                    PriceAnalysisModel.analysis_model == "guided_price_comparison"
                )
            )  # 显示所有市场信息价材料分析结果
            
            db_result = await db.execute(stmt)
            guidance_records = db_result.all()
            
            if not guidance_records:
                # 如果没有实际数据，使用一个简单的示例说明
                return [{
                    "id": "no_data",
                    "material_name": "暂无市场信息价材料数据",
                    "specification": "",
                    "unit": "",
                    "quantity": 0,
                    "original_price": 0,
                    "guidance_price": 0,
                    "original_total_price": 0,
                    "guidance_total_price": 0,
                    "adjustment": 0,
                    "weight_percentage": 0,
                    "material_type": "guidance_price"
                }]
            
            # 计算总金额用于权重计算
            total_amount = 0
            guidance_materials_data = []
            
            for record in guidance_records:
                api_data = record.api_response or {}
                
                # 获取价格数据
                original_price = float(api_data.get('project_unit_price', 0))
                guidance_price = float(api_data.get('base_unit_price', 0))
                # 新增：获取基期信息价和单位，用于前端计算差异
                original_base_price = float(api_data.get('original_base_price', 0) or 0)
                if original_base_price == 0 and guidance_price > 0:
                    # 如果没有基期信息价（旧数据），使用合同期平均价作为基准
                    original_base_price = guidance_price

                base_unit = api_data.get('base_unit', '')

                quantity = float(record.quantity or 0)
                
                # 使用与前端一致的逻辑重新计算差异数据 (AnalysisDetails.vue)
                
                # 1. 风险幅度 (Risk Rate): (合同期平均价 - 基期信息价) / 基期信息价
                # guidance_price 对应 Contract Average Price
                risk_rate_val = 0.0
                if original_base_price > 0:
                    risk_rate_val = (guidance_price - original_base_price) / original_base_price
                risk_rate = risk_rate_val * 100
                
                # 2. 调差 (Adjustment): 超过 +/- 5% 的部分
                adjustment = 0.0
                threshold = 0.05
                
                if risk_rate_val > threshold:
                    excess_per_unit = guidance_price - original_base_price * (1 + threshold)
                    adjustment = excess_per_unit * quantity
                elif risk_rate_val < -threshold:
                    excess_per_unit = guidance_price - original_base_price * (1 - threshold)
                    adjustment = excess_per_unit * quantity
                
                # 3. 价格差异 (Price Diff): 项目单价 - 基期信息价
                # 注意：前端 AnalysisDetails.vue 中 getPricedPriceDifference = project_unit_price - convertedOriginalBasePrice
                price_diff = original_price - original_base_price
                
                original_total = original_price * quantity
                guidance_total = guidance_price * quantity
                
                total_amount += abs(original_total)
                
                guidance_materials_data.append({
                    "record": record,
                    "original_price": original_price,
                    "guidance_price": guidance_price,
                    "original_base_price": original_base_price,
                    "base_unit": base_unit,
                    "quantity": quantity,
                    "original_total": original_total,
                    "guidance_total": guidance_total,
                    "adjustment": adjustment,
                    "price_diff": price_diff,
                    "risk_rate": risk_rate
                })
            
            # 生成最终结果
            for index, item_data in enumerate(guidance_materials_data):
                record = item_data["record"]
                
                # 计算权重百分比
                weight_percentage = (abs(item_data["original_total"]) / total_amount * 100) if total_amount > 0 else 0
                
                material_data = {
                    "id": record.material_id,
                    "material_name": record.material_name or "",
                    "specification": record.specification or "",
                    "unit": record.unit or "",
                    "quantity": item_data["quantity"],
                    "original_price": item_data["original_price"],
                    "guidance_price": item_data["guidance_price"],
                    "original_base_price": item_data["original_base_price"],
                    "base_unit": item_data["base_unit"],
                    "original_total_price": item_data["original_total"],
                    "guidance_total_price": item_data["guidance_total"],
                    "adjustment": item_data["adjustment"],
                    "price_diff": item_data["price_diff"],
                    "risk_rate": item_data["risk_rate"],
                    "weight_percentage": round(weight_percentage, 1),
                    "material_type": "guidance_price"
                }
                
                result.append(material_data)
            
            # 按权重降序排列
            result.sort(key=lambda x: x["weight_percentage"], reverse=True)
            
        except Exception as e:
            logger.error(f"获取市场信息价材料数据失败: {e}")
            # 发生错误时返回空列表或错误提示
            result = [{
                "id": "error",
                "material_name": f"数据获取失败: {str(e)}",
                "specification": "",
                "unit": "",
                "quantity": 0,
                "original_price": 0,
                "guidance_price": 0,
                "original_total_price": 0,
                "guidance_total_price": 0,
                "adjustment": 0,
                "weight_percentage": 0,
                "material_type": "guidance_price"
            }]
        
        return result
