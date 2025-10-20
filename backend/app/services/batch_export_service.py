import asyncio
import zipfile
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from loguru import logger

from app.services.report_service import ReportService
from app.schemas.report import ReportConfigSchema
from app.utils.attachment_manager import AttachmentManager


class BatchExportService:
    """批量报告导出服务"""
    
    def __init__(self):
        self.report_service = ReportService()
        self.attachment_manager = AttachmentManager()
        self.export_dir = Path("exports")
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    async def batch_export_reports(
        self,
        db: AsyncSession,
        project_ids: List[int],
        user_id: int,
        config: Optional[ReportConfigSchema] = None,
        include_attachments: bool = True,
        export_format: str = "zip"
    ) -> str:
        """批量导出报告
        
        Args:
            project_ids: 项目ID列表
            user_id: 用户ID
            config: 报告配置
            include_attachments: 是否包含附件
            export_format: 导出格式 (zip, individual)
        
        Returns:
            导出文件路径
        """
        try:
            if len(project_ids) > 20:  # 限制批量数量
                raise HTTPException(status_code=400, detail="批量导出数量不能超过20个")
            
            export_id = f"batch_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"
            export_folder = self.export_dir / export_id
            export_folder.mkdir(parents=True, exist_ok=True)
            
            # 并发生成报告
            semaphore = asyncio.Semaphore(3)  # 限制并发数
            tasks = []
            
            for project_id in project_ids:
                task = self._generate_single_report_with_semaphore(
                    semaphore, db, project_id, user_id, config, export_folder
                )
                tasks.append(task)
            
            # 等待所有报告生成完成
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 统计结果
            successful_reports = []
            failed_reports = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed_reports.append({
                        'project_id': project_ids[i],
                        'error': str(result)
                    })
                else:
                    successful_reports.append(result)
            
            logger.info(f"批量报告生成完成: 成功{len(successful_reports)}个，失败{len(failed_reports)}个")
            
            # 生成导出结果文件
            export_result = {
                'export_id': export_id,
                'export_time': datetime.now().isoformat(),
                'total_projects': len(project_ids),
                'successful_count': len(successful_reports),
                'failed_count': len(failed_reports),
                'successful_reports': successful_reports,
                'failed_reports': failed_reports
            }
            
            # 保存导出信息
            self._save_export_info(export_folder, export_result)
            
            # 根据格式处理导出文件
            if export_format == "zip":
                zip_path = await self._create_export_archive(
                    export_folder, export_id, include_attachments
                )
                return zip_path
            else:
                return str(export_folder)
                
        except Exception as e:
            logger.error(f"批量导出报告失败: {e}")
            raise HTTPException(status_code=500, detail=f"批量导出失败: {str(e)}")
    
    async def _generate_single_report_with_semaphore(
        self,
        semaphore: asyncio.Semaphore,
        db: AsyncSession,
        project_id: int,
        user_id: int,
        config: Optional[ReportConfigSchema],
        export_folder: Path
    ) -> Dict[str, Any]:
        """使用信号量限制的单个报告生成"""
        async with semaphore:
            try:
                # 生成报告
                report = await self.report_service.generate_report(
                    db=db,
                    project_id=project_id,
                    user_id=user_id,
                    config=config
                )
                
                # 复制报告文件到导出目录
                if report.file_path and Path(report.file_path).exists():
                    dest_filename = f"project_{project_id}_{report.report_title}.docx"
                    dest_path = export_folder / "reports" / dest_filename
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    import shutil
                    shutil.copy2(report.file_path, dest_path)
                    
                    return {
                        'project_id': project_id,
                        'report_id': report.report_id,
                        'report_title': report.report_title,
                        'file_path': str(dest_path),
                        'file_size': report.file_size,
                        'generation_time': report.generation_time
                    }
                else:
                    raise Exception("报告文件不存在")
                    
            except Exception as e:
                logger.error(f"生成项目{project_id}的报告失败: {e}")
                raise Exception(f"项目{project_id}: {str(e)}")
    
    async def _create_export_archive(
        self,
        export_folder: Path,
        export_id: str,
        include_attachments: bool
    ) -> str:
        """创建导出压缩包"""
        try:
            archive_filename = f"{export_id}.zip"
            archive_path = self.export_dir / archive_filename
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 添加报告文件
                reports_folder = export_folder / "reports"
                if reports_folder.exists():
                    for report_file in reports_folder.glob("*.docx"):
                        zipf.write(report_file, f"reports/{report_file.name}")
                
                # 添加导出信息
                export_info_file = export_folder / "export_info.json"
                if export_info_file.exists():
                    zipf.write(export_info_file, "export_info.json")
                
                # 添加附件（如果需要）
                if include_attachments:
                    attachments_folder = export_folder / "attachments"
                    if attachments_folder.exists():
                        for attachment_file in attachments_folder.rglob("*"):
                            if attachment_file.is_file():
                                relative_path = attachment_file.relative_to(export_folder)
                                zipf.write(attachment_file, str(relative_path))
            
            logger.info(f"导出压缩包创建成功: {archive_path}")
            return str(archive_path)
            
        except Exception as e:
            logger.error(f"创建导出压缩包失败: {e}")
            raise
    
    def _save_export_info(self, export_folder: Path, export_result: Dict[str, Any]):
        """保存导出信息"""
        import json
        
        info_file = export_folder / "export_info.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(export_result, f, ensure_ascii=False, indent=2)
    
    async def export_project_comprehensive_package(
        self,
        db: AsyncSession,
        project_id: int,
        user_id: int,
        include_raw_data: bool = True,
        include_analysis_results: bool = True,
        include_attachments: bool = True
    ) -> str:
        """导出项目综合包（包含原始数据、分析结果、报告等）"""
        try:
            package_id = f"comprehensive_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            package_folder = self.export_dir / package_id
            package_folder.mkdir(parents=True, exist_ok=True)
            
            # 1. 生成审计报告
            report = await self.report_service.generate_report(
                db=db,
                project_id=project_id,
                user_id=user_id
            )
            
            if report.file_path and Path(report.file_path).exists():
                reports_folder = package_folder / "reports"
                reports_folder.mkdir(exist_ok=True)
                
                import shutil
                shutil.copy2(report.file_path, reports_folder / "audit_report.docx")
            
            # 2. 导出原始数据（如果需要）
            if include_raw_data:
                await self._export_raw_data(db, project_id, package_folder / "raw_data")
            
            # 3. 导出分析结果（如果需要）
            if include_analysis_results:
                await self._export_analysis_results(db, project_id, package_folder / "analysis")
            
            # 4. 复制附件（如果需要）
            if include_attachments:
                await self._copy_project_attachments(report.report_id, package_folder / "attachments")
            
            # 5. 生成README文件
            self._generate_package_readme(package_folder, project_id)
            
            # 6. 创建压缩包
            archive_path = await self._create_comprehensive_archive(package_folder, package_id)
            
            return archive_path
            
        except Exception as e:
            logger.error(f"导出项目综合包失败: {e}")
            raise HTTPException(status_code=500, detail=f"导出综合包失败: {str(e)}")
    
    async def _export_raw_data(self, db: AsyncSession, project_id: int, output_folder: Path):
        """导出原始数据"""
        output_folder.mkdir(parents=True, exist_ok=True)
        
        from sqlalchemy import select
        from app.models.project import Project, ProjectMaterial
        
        # 导出项目信息
        project_query = select(Project).where(Project.id == project_id)
        result = await db.execute(project_query)
        project = result.scalar_one_or_none()
        
        if project:
            import json
            project_data = {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'status': project.status.value if project.status else None,
                'location': project.location,
                'owner': project.owner,
                'contractor': project.contractor,
                'created_at': project.created_at.isoformat() if project.created_at else None
            }
            
            with open(output_folder / "project_info.json", 'w', encoding='utf-8') as f:
                json.dump(project_data, f, ensure_ascii=False, indent=2)
        
        # 导出材料数据为CSV
        materials_query = select(ProjectMaterial).where(ProjectMaterial.project_id == project_id)
        materials_result = await db.execute(materials_query)
        materials = materials_result.scalars().all()
        
        if materials:
            import pandas as pd
            
            materials_data = []
            for material in materials:
                materials_data.append({
                    'id': material.id,
                    'serial_number': material.serial_number,
                    'material_name': material.material_name,
                    'specification': material.specification,
                    'unit': material.unit,
                    'quantity': material.quantity,
                    'unit_price': material.unit_price,
                    'total_price': material.total_price,
                    'category': material.category,
                    'is_matched': material.is_matched,
                    'is_analyzed': material.is_analyzed,
                    'is_problematic': material.is_problematic
                })
            
            df = pd.DataFrame(materials_data)
            df.to_csv(output_folder / "materials.csv", index=False, encoding='utf-8-sig')
    
    async def _export_analysis_results(self, db: AsyncSession, project_id: int, output_folder: Path):
        """导出分析结果"""
        output_folder.mkdir(parents=True, exist_ok=True)
        
        from sqlalchemy import select
        from app.models.analysis import PriceAnalysis
        from app.models.project import ProjectMaterial
        
        # 获取分析结果
        analysis_query = select(PriceAnalysis).join(ProjectMaterial).where(
            ProjectMaterial.project_id == project_id
        )
        result = await db.execute(analysis_query)
        analyses = result.scalars().all()
        
        if analyses:
            import pandas as pd
            import json
            
            # 导出详细分析结果为JSON
            analysis_data = []
            for analysis in analyses:
                analysis_data.append({
                    'material_id': analysis.material_id,
                    'status': analysis.status.value if analysis.status else None,
                    'predicted_price_min': analysis.predicted_price_min,
                    'predicted_price_max': analysis.predicted_price_max,
                    'predicted_price_avg': analysis.predicted_price_avg,
                    'confidence_score': analysis.confidence_score,
                    'is_reasonable': analysis.is_reasonable,
                    'price_variance': analysis.price_variance,
                    'risk_level': analysis.risk_level,
                    'analysis_model': analysis.analysis_model,
                    'analysis_reasoning': analysis.analysis_reasoning,
                    'risk_factors': analysis.risk_factors,
                    'recommendations': analysis.recommendations,
                    'analysis_cost': analysis.analysis_cost,
                    'analysis_time': analysis.analysis_time,
                    'created_at': analysis.created_at.isoformat() if analysis.created_at else None
                })
            
            with open(output_folder / "analysis_results.json", 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            
            # 导出汇总统计为CSV
            summary_data = []
            for analysis in analyses:
                summary_data.append({
                    'material_id': analysis.material_id,
                    'predicted_price_avg': analysis.predicted_price_avg,
                    'confidence_score': analysis.confidence_score,
                    'is_reasonable': analysis.is_reasonable,
                    'price_variance': analysis.price_variance,
                    'risk_level': analysis.risk_level
                })
            
            df = pd.DataFrame(summary_data)
            df.to_csv(output_folder / "analysis_summary.csv", index=False, encoding='utf-8-sig')
    
    async def _copy_project_attachments(self, report_id: int, output_folder: Path):
        """复制项目附件"""
        output_folder.mkdir(parents=True, exist_ok=True)
        
        attachments = self.attachment_manager.get_report_attachments(report_id)
        
        if attachments:
            import shutil
            
            for attachment in attachments:
                if Path(attachment['file_path']).exists():
                    dest_path = output_folder / attachment['original_filename']
                    shutil.copy2(attachment['file_path'], dest_path)
    
    def _generate_package_readme(self, package_folder: Path, project_id: int):
        """生成综合包说明文件"""
        readme_content = f"""# 项目 {project_id} 综合导出包

## 文件夹结构

- `/reports/` - 审计报告
  - `audit_report.docx` - 完整审计报告

- `/raw_data/` - 原始数据
  - `project_info.json` - 项目基本信息
  - `materials.csv` - 材料清单数据

- `/analysis/` - 分析结果
  - `analysis_results.json` - 详细分析结果
  - `analysis_summary.csv` - 分析结果汇总

- `/attachments/` - 相关附件
  - 各种支撑文档和附件文件

## 导出时间
{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

## 使用说明
1. 审计报告是主要成果文档
2. 原始数据可用于重新分析
3. 分析结果包含AI分析的详细信息
4. 附件提供额外的参考资料

## 技术说明
本导出包由造价材料审计系统自动生成，包含项目的完整数据和分析结果。
        """
        
        with open(package_folder / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    async def _create_comprehensive_archive(self, package_folder: Path, package_id: str) -> str:
        """创建综合包压缩文件"""
        archive_path = self.export_dir / f"{package_id}.zip"
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in package_folder.rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(package_folder)
                    zipf.write(file_path, str(relative_path))
        
        return str(archive_path)