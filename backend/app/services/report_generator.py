import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import json

from docx import Document
from docx.shared import Inches, Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_PARAGRAPH_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.section import WD_SECTION, WD_ORIENT
from docx.oxml.shared import OxmlElement, qn
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import rcParams
import seaborn as sns
import pandas as pd
from io import BytesIO
import base64

from app.core.config import settings
from app.models.analysis import AuditReport
from app.models.project import Project, ProjectMaterial
from app.models.analysis import PriceAnalysis
from loguru import logger


class ReportGenerator:
    """审计报告生成器"""
    
    def __init__(self):
        self.templates_dir = Path("templates")
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置matplotlib中文支持
        rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        rcParams['axes.unicode_minus'] = False
        
    async def generate_audit_report(
        self,
        db: AsyncSession,
        project: Project,
        materials: List[ProjectMaterial],
        analyses: List[PriceAnalysis],
        report_config: Dict[str, Any] = None
    ) -> str:
        """生成完整的审计报告
        
        Args:
            project: 项目信息
            materials: 项目材料列表
            analyses: 价格分析结果
            report_config: 报告配置参数
            
        Returns:
            报告文件路径
        """
        try:
            # 生成报告数据
            report_data = await self._prepare_report_data(db, project, materials, analyses)

            # 创建Word文档
            doc = Document()

            # 添加报告标题页
            self._add_title_page(doc, report_data)

            # 添加执行摘要
            self._add_executive_summary(doc, report_data)

            # 添加项目概况
            self._add_project_overview(doc, report_data)

            # 添加分析方法与数据来源
            self._add_methodology_section(doc, report_data)

            # 添加分析结果
            await self._add_analysis_results(doc, report_data)

            # 添加问题材料详情
            self._add_problematic_materials(doc, report_data)

            # 添加图表分析
            chart_files = self._generate_charts(report_data)
            self._add_charts_to_document(doc, chart_files)

            # 添加建议措施
            self._add_recommendations(doc, report_data)

            # 添加附录
            self._add_appendices(doc, report_data)

            # 保存报告
            report_filename = f"audit_report_{project.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
            report_path = self.reports_dir / report_filename
            doc.save(str(report_path))

            logger.info(f"审计报告生成成功: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"生成审计报告失败: {e}")
            raise
    
    async def _prepare_report_data(
        self,
        db: AsyncSession,
        project: Project,
        materials: List[ProjectMaterial],
        analyses: List[PriceAnalysis]
    ) -> Dict[str, Any]:
        """准备报告数据"""

        total_materials = len(materials)

        price_analyses = {a.material_id: a for a in analyses}

        analyzed_ids_from_flag = {m.id for m in materials if getattr(m, 'is_analyzed', False)}
        analyzed_ids_from_analysis = {a.material_id for a in analyses if a is not None}
        analyzed_materials = len(analyzed_ids_from_flag | analyzed_ids_from_analysis)

        problematic_from_material = {m.id for m in materials if getattr(m, 'is_problematic', False)}
        problematic_from_analysis = {a.material_id for a in analyses if a and a.is_reasonable is False}
        problematic_materials = len(problematic_from_material | problematic_from_analysis)
        unreasonable_count = len(problematic_from_analysis)

        def infer_risk_level(a: Optional[PriceAnalysis]) -> str:
            if not a:
                return 'unknown'
            if a.risk_level:
                return a.risk_level
            try:
                variance = abs(a.price_variance or 0)
                if variance >= 60:
                    return 'critical'
                if variance >= 40:
                    return 'high'
                if variance >= 20:
                    return 'medium'
                if variance > 0:
                    return 'low'
                return 'normal'
            except Exception:
                return 'unknown'

        risk_stats: Dict[str, int] = {}
        for analysis in analyses:
            level = infer_risk_level(analysis)
            risk_stats[level] = risk_stats.get(level, 0) + 1

        price_variances = [a.price_variance for a in analyses if a and a.price_variance is not None]
        avg_variance = sum(price_variances) / len(price_variances) if price_variances else 0

        estimated_savings = 0
        for material in materials:
            analysis = price_analyses.get(material.id)
            if analysis and analysis.predicted_price_avg and material.unit_price:
                if material.unit_price > analysis.predicted_price_avg:
                    savings = (material.unit_price - analysis.predicted_price_avg) * (material.quantity or 0)
                    estimated_savings += savings

        from app.services.report_service import ReportService
        report_service = ReportService()

        analysis_materials_raw = report_service._generate_analysis_materials_data(materials, analyses)
        guidance_materials_raw = await report_service._generate_guidance_price_materials_data(
            db, project.id, materials, analyses
        )

        def transform_analysis_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            transformed: List[Dict[str, Any]] = []
            for item in items:
                quantity = float(item.get('quantity') or 0)
                original_unit = float(item.get('original_price') or 0)
                ai_unit = float(item.get('ai_predicted_price') or item.get('predicted_price') or 0)
                original_total = float(item.get('original_total_price') or (original_unit * quantity))
                ai_total = float(item.get('ai_total_price') or item.get('ai_total') or (ai_unit * quantity))
                adjustment = float(item.get('adjustment')) if item.get('adjustment') is not None else original_total - ai_total
                risk_level = (item.get('risk_level') or '').lower()
                is_reasonable = item.get('is_reasonable')

                has_difference = abs(adjustment) > 1e-2
                has_risk = (risk_level not in ('', 'normal', 'low')) or (is_reasonable is False)
                if not (has_difference or has_risk):
                    continue

                transformed.append({
                    'materialName': item.get('material_name', ''),
                    'specification': item.get('specification', ''),
                    'unit': item.get('unit', ''),
                    'quantity': quantity,
                    'originalUnitPrice': original_unit,
                    'originalTotalPrice': original_total,
                    'aiUnitPrice': ai_unit,
                    'aiTotalPrice': ai_total,
                    'adjustment': adjustment,
                    'weightPercentage': 0.0,
                    'riskLevel': risk_level or 'normal'
                })

            total_original = sum(abs(item['originalTotalPrice']) for item in transformed)
            if total_original > 0:
                for item in transformed:
                    item['weightPercentage'] = (abs(item['originalTotalPrice']) / total_original) * 100

            return transformed

        def transform_guidance_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            transformed: List[Dict[str, Any]] = []
            for item in items:
                if item.get('material_name') in ['暂无市场信息价材料数据', '数据获取失败', None, '']:
                    continue

                quantity = float(item.get('quantity') or 0)
                original_unit = float(item.get('original_price') or 0)
                guidance_unit = float(item.get('guidance_price') or item.get('base_price') or 0)
                original_total = float(item.get('original_total_price') or (original_unit * quantity))
                guidance_total = float(item.get('guidance_total_price') or item.get('ai_total_price') or (guidance_unit * quantity))
                adjustment = float(item.get('adjustment')) if item.get('adjustment') is not None else original_total - guidance_total

                if abs(adjustment) <= 1e-2:
                    continue

                transformed.append({
                    'materialName': item.get('material_name', ''),
                    'specification': item.get('specification', ''),
                    'unit': item.get('unit', ''),
                    'quantity': quantity,
                    'originalUnitPrice': original_unit,
                    'originalTotalPrice': original_total,
                    'aiUnitPrice': guidance_unit,
                    'aiTotalPrice': guidance_total,
                    'adjustment': adjustment,
                    'weightPercentage': 0.0
                })

            total_original = sum(abs(item['originalTotalPrice']) for item in transformed)
            if total_original > 0:
                for item in transformed:
                    item['weightPercentage'] = (abs(item['originalTotalPrice']) / total_original) * 100

            return transformed

        analysis_materials_report = transform_analysis_items(analysis_materials_raw)
        guidance_materials_report = transform_guidance_items(guidance_materials_raw)

        def calc_totals(items: List[Dict[str, Any]]) -> Dict[str, float]:
            return {
                'original_total': sum(item['originalTotalPrice'] for item in items),
                'ai_total': sum(item['aiTotalPrice'] for item in items),
                'adjustment_total': sum(item['adjustment'] for item in items)
            }

        analysis_totals = calc_totals(analysis_materials_report)
        guidance_totals = calc_totals(guidance_materials_report)

        combined_adjustments = []
        for item in analysis_materials_report:
            combined_adjustments.append((item['materialName'], item['adjustment']))
        for item in guidance_materials_report:
            combined_adjustments.append((item['materialName'], item['adjustment']))

        combined_adjustments.sort(key=lambda x: abs(x[1]), reverse=True)
        top_adjustments = combined_adjustments[:5]

        risk_label_map = {
            'normal': '正常',
            'low': '低风险',
            'medium': '中风险',
            'high': '高风险',
            'critical': '极高风险',
            'severe': '极高风险',
            'unknown': '待确认'
        }
        risk_distribution = {
            risk_label_map.get(level, level): count
            for level, count in risk_stats.items()
        }

        return {
            'project': project,
            'db': db,
            'report_date': datetime.now(),
            'statistics': {
                'total_materials': total_materials,
                'analyzed_materials': analyzed_materials,
                'problematic_materials': problematic_materials,
                'unreasonable_count': unreasonable_count,
                'analysis_coverage': (analyzed_materials / total_materials * 100) if total_materials > 0 else 0,
                'problem_rate': (problematic_materials / total_materials * 100) if total_materials > 0 else 0,
                'avg_price_variance': avg_variance,
                'estimated_savings': estimated_savings,
                'analysis_totals': analysis_totals,
                'guidance_totals': guidance_totals
            },
            'risk_stats_raw': risk_stats,
            'risk_stats': risk_distribution,
            'materials': materials,
            'analyses': analyses,
            'price_analyses': price_analyses,
            'analysis_materials_report': analysis_materials_report,
            'guidance_materials_report': guidance_materials_report,
            'top_adjustments': top_adjustments
        }
    
    def _add_title_page(self, doc: Document, data: Dict[str, Any]):
        """添加报告标题页"""
        project = data['project']
        
        # 标题
        title = doc.add_heading('造价材料审计报告', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph()
        
        # 项目信息表
        table = doc.add_table(rows=6, cols=2)
        table.style = 'Table Grid'
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        cells = table.rows[0].cells
        cells[0].text = '项目名称'
        cells[1].text = project.name or ''
        
        cells = table.rows[1].cells
        cells[0].text = '项目编号'
        cells[1].text = project.project_code or ''
        
        cells = table.rows[2].cells
        cells[0].text = '项目地点'
        cells[1].text = project.location or ''
        
        cells = table.rows[3].cells
        cells[0].text = '业主单位'
        cells[1].text = project.owner or ''
        
        cells = table.rows[4].cells
        cells[0].text = '承包单位'
        cells[1].text = project.contractor or ''
        
        cells = table.rows[5].cells
        cells[0].text = '报告日期'
        cells[1].text = data['report_date'].strftime('%Y年%m月%d日')
        
        doc.add_page_break()
    
    def _add_executive_summary(self, doc: Document, data: Dict[str, Any]):
        """添加执行摘要"""
        doc.add_heading('执行摘要', 1)
        
        stats = data['statistics']
        top_adjustments = data.get('top_adjustments', [])

        overview_para = doc.add_paragraph()
        run = overview_para.add_run('总体结论：')
        run.bold = True
        run.font.name = 'SimHei'
        run.font.size = Pt(11)
        overview_para.add_run(
            f" 本次对项目共审查 {stats['total_materials']} 项材料，其中 {stats['analyzed_materials']} 项完成价格分析，"
            f"分析覆盖率 {stats['analysis_coverage']:.1f}%。检测到 {stats['problematic_materials']} 项存在风险，"
            f"问题发现率 {stats['problem_rate']:.1f}%，其中 {stats['unreasonable_count']} 项价格被判定为不合理。"
        )

        highlight_para = doc.add_paragraph()
        highlight_para.add_run('关键指标：').bold = True
        metrics = doc.add_table(rows=2, cols=3)
        metrics.style = 'Table Grid'
        metric_items = [
            ('平均价格偏差', f"{stats['avg_price_variance']:.2f}%"),
            ('预估节约金额', f"{stats['estimated_savings']:.2f} 元"),
            ('送审总额（无信息价）', f"{stats['analysis_totals']['original_total']:,.2f} 元")
        ]
        metric_items.extend([
            ('AI核审总额（无信息价）', f"{stats['analysis_totals']['ai_total']:,.2f} 元"),
            ('送审总额（市场信息价）', f"{stats['guidance_totals']['original_total']:,.2f} 元"),
            ('AI核审总额（市场信息价）', f"{stats['guidance_totals']['ai_total']:,.2f} 元")
        ])
        for idx, (label, value) in enumerate(metric_items):
            row = metrics.rows[idx // 3]
            cell = row.cells[idx % 3]
            cell.text = f"{label}\n{value}"
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            run = cell.paragraphs[0].runs[0]
            run.font.name = 'SimSun'
            run.font.size = Pt(9)

        doc.add_paragraph()

        if top_adjustments:
            doc.add_paragraph('重点关注材料（按核增减额排序）：').runs[0].bold = True
            for name, value in top_adjustments:
                para = doc.add_paragraph(style='List Bullet')
                para.add_run(f"{name}：核增减额 {value:+,.2f} 元")

        doc.add_paragraph(
            '建议优先对高风险及金额差异较大的材料进行复核和询价，必要时补充市场调查或合同条款校验，确保成本控制在合理范围。'
        )

        doc.add_page_break()
    
    def _add_project_overview(self, doc: Document, data: Dict[str, Any]):
        """添加项目概况"""
        doc.add_heading('项目概况', 1)
        
        project = data['project']
        stats = data['statistics']
        
        # 项目基本信息
        doc.add_heading('基本信息', 2)
        
        info_text = f"""
项目名称：{project.name}
项目编号：{project.project_code or '未提供'}
项目地点：{project.location or '未提供'}
业主单位：{project.owner or '未提供'}
承包单位：{project.contractor or '未提供'}
项目状态：{project.status.value if project.status else '未知'}
创建时间：{project.created_at.strftime('%Y年%m月%d日') if project.created_at else '未知'}
        """
        
        doc.add_paragraph(info_text.strip())
        
        # 材料统计
        doc.add_heading('材料统计', 2)
        
        stats_table = doc.add_table(rows=5, cols=2)
        stats_table.style = 'Table Grid'
        
        stats_data = [
            ('材料总数', f"{stats['total_materials']}项"),
            ('已分析材料', f"{stats['analyzed_materials']}项"),
            ('问题材料', f"{stats['problematic_materials']}项"),
            ('分析覆盖率', f"{stats['analysis_coverage']:.1f}%"),
            ('问题发现率', f"{stats['problem_rate']:.1f}%")
        ]
        
        for i, (label, value) in enumerate(stats_data):
            cells = stats_table.rows[i].cells
            cells[0].text = label
            cells[1].text = value

    def _add_methodology_section(self, doc: Document, data: Dict[str, Any]):
        """添加分析方法与数据来源说明"""
        doc.add_heading('分析方法与数据来源', 1)

        method_para = doc.add_paragraph()
        method_para.add_run('分析流程：').bold = True
        method_para.add_run(
            ' 1) 基于项目材料清单提取无信息价材料与匹配的市场信息价材料；'
            ' 2) 对无信息价材料调用 AI 价格分析模型，生成推荐单价区间及合理性判断；'
            ' 3) 对市场信息价材料按照区县→市→省三级层次匹配最新信息价；'
            ' 4) 比对送审价格与 AI/市场价格，形成核增减额、风险等级和建议。'
        )

        data_para = doc.add_paragraph()
        data_para.add_run('数据来源：').bold = True
        data_para.add_run(
            ' 项目材料数据来自系统上传的清单；信息价数据引用平台最新刊期；'
            ' AI 模型训练及单位换算遵循系统既定规则，自动记录分析时间与参数。'
        )

        assumptions = doc.add_paragraph()
        assumptions.add_run('校验说明：').bold = True
        assumptions.add_run(
            ' 报告生成时自动校验计量单位、数量、价格区间，若存在缺失或异常数据，将在问题材料章节提示人工复核。'
        )

        doc.add_paragraph()

    async def _add_analysis_results(self, doc: Document, data: Dict[str, Any]):
        """添加分析结果"""
        doc.add_heading('分析结果', 1)
        
        project = data['project']
        analysis_materials = data.get('analysis_materials_report', [])
        guidance_materials = data.get('guidance_materials_report', [])
        stats = data.get('statistics', {})

        doc.add_paragraph(
            f"本节汇总无信息价材料与市场信息价材料的价格对比情况，并列出存在较大差异或风险的材料明细。"
        )

        # 差额概况
        analysis_totals = stats.get('analysis_totals', {})
        guidance_totals = stats.get('guidance_totals', {})

        overview_table = doc.add_table(rows=3, cols=4)
        overview_table.style = 'Table Grid'
        headers = ['类别', '送审总额（元）', 'AI核审总额（元）', '核增减额（元）']
        for idx, header in enumerate(headers):
            cell = overview_table.rows[0].cells[idx]
            cell.text = header
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            run = cell.paragraphs[0].runs[0]
            run.font.name = 'SimHei'
            run.font.size = Pt(9)
            run.bold = True

        overview_rows = [
            ('无信息价材料', analysis_totals.get('original_total', 0), analysis_totals.get('ai_total', 0), analysis_totals.get('adjustment_total', 0)),
            ('市场信息价材料', guidance_totals.get('original_total', 0), guidance_totals.get('ai_total', 0), guidance_totals.get('adjustment_total', 0))
        ]

        for row_idx, row_data in enumerate(overview_rows, start=1):
            row = overview_table.rows[row_idx]
            row.cells[0].text = row_data[0]
            row.cells[1].text = f"{row_data[1]:,.2f}"
            row.cells[2].text = f"{row_data[2]:,.2f}"
            row.cells[3].text = f"{row_data[3]:+,.2f}"
            for cell in row.cells:
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                run = cell.paragraphs[0].runs[0]
                run.font.name = 'SimSun'
                run.font.size = Pt(9)

        doc.add_paragraph()

        # 生成表1：材料价格分析表（无信息价材料）
        if analysis_materials:
            self.create_standard_material_table(
                doc, 
                "表1 材料价格分析表（无信息价材料）", 
                analysis_materials,
                "analysis",
                project.name or "未命名项目"
            )

        # 生成表2：材料价格分析表（市场信息价材料）
        if guidance_materials:
            self.create_standard_material_table(
                doc, 
                "表2 材料价格分析表（市场信息价材料）", 
                guidance_materials,  # 显示所有数据
                "guidance_price",
                project.name or "未命名项目"
            )
        elif not guidance_materials:
            # 如果没有市场信息价材料，显示提示信息
            doc.add_paragraph("暂无市场信息价材料数据")
        
        # 风险等级分布摘要
        doc.add_heading('风险等级分布', 2)
        
        risk_stats = data.get('risk_stats', {})
        if risk_stats:
            risk_table = doc.add_table(rows=len(risk_stats) + 1, cols=2)
            risk_table.style = 'Table Grid'
            
            # 表头
            cells = risk_table.rows[0].cells
            cells[0].text = '风险等级'
            cells[1].text = '材料数量'
            
            # 数据行
            for i, (risk_level, count) in enumerate(risk_stats.items(), 1):
                cells = risk_table.rows[i].cells
                cells[0].text = risk_level
                cells[1].text = f"{count}项"
        
        # 价格分析汇总
        doc.add_heading('价格分析汇总', 2)
        
        stats = data.get('statistics', {})
        summary_text = f"""
• 平均价格偏差：{stats.get('avg_price_variance', 0):.2f}%
• 不合理价格材料：{stats.get('unreasonable_count', 0)}项
• 预估节约金额：{stats.get('estimated_savings', 0):.2f}元
        """
        
        doc.add_paragraph(summary_text.strip())
    
    def _add_problematic_materials(self, doc: Document, data: Dict[str, Any]):
        """添加问题材料详情"""
        doc.add_heading('问题材料详情', 1)
        
        materials = data['materials']
        price_analyses = data['price_analyses']
        
        # 筛选问题材料
        problematic_materials = [m for m in materials if m.is_problematic]
        
        if not problematic_materials:
            doc.add_paragraph('未发现问题材料。')
            return
        
        # 创建问题材料表格
        table = doc.add_table(rows=len(problematic_materials) + 1, cols=6)
        table.style = 'Table Grid'
        
        # 表头
        headers = ['序号', '材料名称', '规格', '单价', '风险等级', '问题描述']
        for i, header in enumerate(headers):
            table.rows[0].cells[i].text = header
        
        # 数据行
        for i, material in enumerate(problematic_materials, 1):
            cells = table.rows[i].cells
            cells[0].text = str(i)
            cells[1].text = material.material_name
            cells[2].text = material.specification or ''
            cells[3].text = f"{material.unit_price:.2f}" if material.unit_price else ''
            
            # 获取风险等级和问题描述
            if material.id in price_analyses:
                analysis = price_analyses[material.id]
                cells[4].text = analysis.risk_level or ''
                
                # 生成问题描述
                problems = []
                if analysis.is_reasonable == False:
                    problems.append('价格不合理')
                if analysis.price_variance and abs(analysis.price_variance) > 30:
                    problems.append(f'价格偏差{analysis.price_variance:.1f}%')
                
                cells[5].text = '；'.join(problems) or '需要人工确认'
            else:
                cells[4].text = '未分析'
                cells[5].text = '缺少价格分析'
    
    def _generate_charts(self, data: Dict[str, Any]) -> List[str]:
        """生成图表文件"""
        chart_files = []
        
        try:
            chart_path = self._create_risk_level_pie_chart(data)
            if chart_path:
                chart_files.append(chart_path)
            
            chart_path = self._create_adjustment_top_chart(data)
            if chart_path:
                chart_files.append(chart_path)

            chart_path = self._create_total_comparison_chart(data)
            if chart_path:
                chart_files.append(chart_path)
                
        except Exception as e:
            logger.error(f"生成图表失败: {e}")
        
        return chart_files
    
    def _create_risk_level_pie_chart(self, data: Dict[str, Any]) -> Optional[str]:
        """创建风险等级饼图"""
        risk_stats = data.get('risk_stats_raw', {})
        if not risk_stats:
            return None
        
        # 准备数据
        label_map = {
            'normal': '正常',
            'low': '低风险',
            'medium': '中风险',
            'high': '高风险',
            'critical': '极高风险',
            'severe': '极高风险',
            'unknown': '待确认'
        }
        color_map = {
            'normal': '#67C23A',
            'low': '#409EFF',
            'medium': '#E6A23C',
            'high': '#F56C6C',
            'critical': '#C039A5',
            'severe': '#C039A5',
            'unknown': '#909399'
        }

        ordered_levels = ['normal', 'low', 'medium', 'high', 'critical', 'unknown']
        labels = []
        sizes = []
        colors = []
        for level in ordered_levels:
            if level in risk_stats:
                labels.append(label_map.get(level, level))
                sizes.append(risk_stats[level])
                colors.append(color_map.get(level, '#409EFF'))

        # 创建饼图
        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=labels, colors=colors[:len(labels)], autopct='%1.1f%%', startangle=90)
        plt.title('材料风险等级分布', fontsize=16)
        plt.axis('equal')
        
        # 保存图表
        chart_filename = f"risk_levels_{uuid.uuid4().hex[:8]}.png"
        chart_path = self.reports_dir / chart_filename
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(chart_path)

    def _create_adjustment_top_chart(self, data: Dict[str, Any]) -> Optional[str]:
        items: List[Tuple[str, float]] = []
        for item in data.get('analysis_materials_report', []):
            items.append((item['materialName'], item['adjustment']))
        for item in data.get('guidance_materials_report', []):
            items.append((item['materialName'], item['adjustment']))

        if not items:
            return None

        items.sort(key=lambda x: abs(x[1]), reverse=True)
        top_items = items[:10]
        names = [name for name, _ in top_items][::-1]
        values = [value for _, value in top_items][::-1]
        colors = ['#F56C6C' if v > 0 else '#67C23A' for v in values]

        plt.figure(figsize=(12, 7))
        bars = plt.barh(names, values, color=colors)
        plt.title('核增减额TOP10', fontsize=16)
        plt.xlabel('金额（元）', fontsize=12)
        plt.grid(axis='x', alpha=0.2)
        plt.axvline(0, color='#333', linewidth=0.8)

        max_value = max((abs(v) for v in values), default=0)
        offset = max_value * 0.02 if max_value else 0
        for bar, value in zip(bars, values):
            x_pos = value + offset if value >= 0 else value - offset
            ha = 'left' if value >= 0 else 'right'
            plt.text(x_pos, bar.get_y() + bar.get_height() / 2, f"{value:+,.2f}", va='center', ha=ha, fontsize=9)

        plt.tight_layout()

        chart_filename = f"adjustment_top_{uuid.uuid4().hex[:8]}.png"
        chart_path = self.reports_dir / chart_filename
        plt.savefig(chart_path, dpi=300)
        plt.close()

        return str(chart_path)

    def _create_total_comparison_chart(self, data: Dict[str, Any]) -> Optional[str]:
        stats = data.get('statistics', {})
        analysis_totals = stats.get('analysis_totals') or {}
        guidance_totals = stats.get('guidance_totals') or {}

        categories = ['无信息价材料', '市场信息价材料']
        original_totals = [analysis_totals.get('original_total', 0), guidance_totals.get('original_total', 0)]
        ai_totals = [analysis_totals.get('ai_total', 0), guidance_totals.get('ai_total', 0)]

        if not any(original_totals) and not any(ai_totals):
            return None

        x = range(len(categories))
        width = 0.35

        plt.figure(figsize=(10, 6))
        plt.bar([i - width / 2 for i in x], original_totals, width, label='送审总额', color='#409EFF')
        plt.bar([i + width / 2 for i in x], ai_totals, width, label='AI核审总额', color='#67C23A')

        plt.xticks(list(x), categories)
        plt.ylabel('金额（元）')
        plt.title('送审 VS AI 核审 总额对比', fontsize=16)
        plt.legend()
        plt.grid(axis='y', alpha=0.2)

        for idx, value in enumerate(original_totals):
            plt.text(idx - width / 2, value, f"{value:,.2f}", ha='center', va='bottom', fontsize=9)
        for idx, value in enumerate(ai_totals):
            plt.text(idx + width / 2, value, f"{value:,.2f}", ha='center', va='bottom', fontsize=9)

        plt.tight_layout()

        chart_filename = f"totals_compare_{uuid.uuid4().hex[:8]}.png"
        chart_path = self.reports_dir / chart_filename
        plt.savefig(chart_path, dpi=300)
        plt.close()

        return str(chart_path)
    def _create_price_variance_chart(self, data: Dict[str, Any]) -> Optional[str]:
        """创建价格偏差分析图"""
        analyses = data['analyses']
        if not analyses:
            return None
        
        # 准备数据
        variances = []
        materials = []
        
        for i, analysis in enumerate(analyses[:20]):  # 只显示前20个
            if analysis.price_variance is not None:
                variances.append(analysis.price_variance)
                materials.append(f"材料{i+1}")
        
        if len(variances) < 2:
            return None
        
        # 创建条形图
        plt.figure(figsize=(12, 6))
        colors = ['red' if v > 30 else 'orange' if v > 15 else 'green' for v in variances]
        plt.bar(materials, variances, color=colors, alpha=0.7)
        plt.title('材料价格偏差分析', fontsize=16)
        plt.xlabel('材料', fontsize=12)
        plt.ylabel('价格偏差（%）', fontsize=12)
        plt.xticks(rotation=45)
        plt.axhline(y=15, color='orange', linestyle='--', alpha=0.5, label='15%警戒线')
        plt.axhline(y=30, color='red', linestyle='--', alpha=0.5, label='30%风险线')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 保存图表
        chart_filename = f"price_variance_{uuid.uuid4().hex[:8]}.png"
        chart_path = self.reports_dir / chart_filename
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(chart_path)
    
    def _add_charts_to_document(self, doc: Document, chart_files: List[str]):
        """将图表添加到文档中"""
        if not chart_files:
            return
        
        doc.add_heading('图表分析', 1)
        
        for chart_file in chart_files:
            if os.path.exists(chart_file):
                try:
                    doc.add_picture(chart_file, width=Inches(6))
                    doc.add_paragraph()  # 添加间距
                except Exception as e:
                    logger.error(f"添加图表失败 {chart_file}: {e}")
        
        doc.add_page_break()
    
    def _add_recommendations(self, doc: Document, data: Dict[str, Any]):
        """添加建议措施"""
        doc.add_heading('建议措施', 1)
        
        stats = data['statistics']
        
        recommendations = []
        
        if stats['problem_rate'] > 10:
            recommendations.append(
                "发现较多价格异常材料，建议加强供应商管理和价格监控。"
            )
        
        if stats['avg_price_variance'] > 20:
            recommendations.append(
                f"平均价格偏差达到{stats['avg_price_variance']:.1f}%，超出正常范围，"
                "建议重新核实市场价格。"
            )
        
        if stats['estimated_savings'] > 10000:
            recommendations.append(
                f"预估可节约成本{stats['estimated_savings']:.2f}元，建议优化采购策略。"
            )
        
        # 通用建议
        recommendations.extend([
            "定期更新基准材料价格数据库，确保价格信息的时效性。",
            "建立材料价格预警机制，及时发现价格异常。",
            "加强与供应商的沟通，了解价格变动原因。",
            "对高风险材料进行重点监控和审核。"
        ])
        
        for i, rec in enumerate(recommendations, 1):
            doc.add_paragraph(f"{i}. {rec}")
    
    def _add_appendices(self, doc: Document, data: Dict[str, Any]):
        """添加附录"""
        doc.add_heading('附录', 1)
        
        # 附录A: 技术说明
        doc.add_heading('附录A：技术说明', 2)
        
        tech_info = """
本报告使用人工智能技术进行材料价格分析，主要技术特点如下：

1. 多AI服务集成：支持OpenAI GPT-4、通义千问等多个AI服务。
2. 智能匹配算法：基于材料名称、规格、单位等多维度进行相似度计算。
3. 价格合理性分析：结合统计学方法和AI预测进行综合判断。
4. 故障转移机制：确保分析服务的高可用性。

分析结果仅供参考，最终决策请结合实际情况和专业判断。
        """
        
        doc.add_paragraph(tech_info.strip())
        
        # 附录B: 数据统计
        doc.add_heading('附录B：详细统计', 2)
        
        analyses = data['analyses']
        if analyses:
            # AI服务使用统计
            ai_providers = {}
            for analysis in analyses:
                provider = analysis.analysis_model or 'unknown'
                ai_providers[provider] = ai_providers.get(provider, 0) + 1
            
            doc.add_paragraph("AI服务使用统计：")
            for provider, count in ai_providers.items():
                doc.add_paragraph(f"• {provider}: {count}次")
    
    def _set_table_borders(self, table):
        """设置表格边框"""
        tbl = table._tbl
        for cell in table._cells:
            tc = cell._tc
            tcPr = tc.get_or_add_tcPr()
            
            # 创建边框元素
            tcBorders = OxmlElement('w:tcBorders')
            
            # 设置所有边框
            for border_name in ['top', 'left', 'bottom', 'right']:
                border = OxmlElement(f'w:{border_name}')
                border.set(qn('w:val'), 'single')
                border.set(qn('w:sz'), '4')  # 边框粗细
                border.set(qn('w:space'), '0')
                border.set(qn('w:color'), '000000')  # 黑色边框
                tcBorders.append(border)
            
            tcPr.append(tcBorders)
    
    def _merge_cells_horizontally(self, table, row_idx, start_col, end_col):
        """水平合并单元格"""
        if start_col >= end_col:
            return
        
        # 获取要合并的单元格
        cells = table.rows[row_idx].cells
        main_cell = cells[start_col]
        
        # 合并后续单元格
        for col_idx in range(start_col + 1, end_col + 1):
            if col_idx < len(cells):
                main_cell.merge(cells[col_idx])
    
    def create_standard_material_table(self, doc: Document, title: str, materials_data: List[Dict], 
                                     table_type: str = "analysis", project_name: str = "") -> None:
        """创建标准化的材料分析表格
        
        Args:
            doc: Word文档对象
            title: 表格标题
            materials_data: 材料数据列表
            table_type: 表格类型 ("analysis" 或 "guidance_price")
            project_name: 项目名称
        """
        # 插入新的分节符，设置为横向
        if len(doc.sections) > 0:
            doc.add_section(WD_SECTION.NEW_PAGE)
        
        # 设置当前节为横向
        current_section = doc.sections[-1]
        current_section.orientation = WD_ORIENT.LANDSCAPE
        
        # 设置横向页面的页边距（交换宽度和高度的概念）
        current_section.page_height = Cm(21)    # A4纸宽度
        current_section.page_width = Cm(29.7)   # A4纸长度
        current_section.left_margin = Cm(1.5)
        current_section.right_margin = Cm(1.5)
        current_section.top_margin = Cm(1.5)
        current_section.bottom_margin = Cm(1.5)
        
        # 添加表格标题
        heading = doc.add_heading(title, level=2)
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # 设置标题字体为黑体
        for run in heading.runs:
            run.font.name = 'SimHei'  # 黑体
            run.font.size = Pt(14)
            run.bold = True
        
        # 添加项目信息和单位信息在同一行
        project_info = doc.add_paragraph()
        
        # 左侧项目名称
        run1 = project_info.add_run("项目名称：")
        run1.bold = True
        run1.font.name = 'SimSun'  # 宋体
        run1.font.size = Pt(10)
        
        run2 = project_info.add_run(project_name or "未命名项目")
        run2.font.name = 'SimSun'
        run2.font.size = Pt(10)
        
        # 添加制表符来推送"单位：元"到右侧
        from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
        
        # 设置制表位到页面右侧
        tab_stops = project_info.paragraph_format.tab_stops
        tab_stops.add_tab_stop(Cm(25), WD_TAB_ALIGNMENT.RIGHT)  # 25cm处右对齐制表位
        
        # 添加制表符和单位信息
        run3 = project_info.add_run("\t单位：元")
        run3.bold = True
        run3.font.name = 'SimSun'
        run3.font.size = Pt(10)
        
        # 创建表格 - 基础列数
        base_cols = 11  # 序号、材料名称、规格型号、单位、数量、送审结算(单价/合价)、AI辅助审核(单价/合价)、核增减额、权重
        
        # 创建表格
        table = doc.add_table(rows=2, cols=base_cols)
        table.style = 'Table Grid'
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # 设置表格边框样式（全边框）
        from docx.oxml.ns import nsdecls
        from docx.oxml import parse_xml
        
        tbl = table._tbl
        tblPr = tbl.tblPr
        tblBorders = parse_xml(r'<w:tblBorders {}>'
                              r'<w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
                              r'<w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
                              r'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
                              r'<w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
                              r'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
                              r'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
                              r'</w:tblBorders>'.format(nsdecls('w')))
        tblPr.append(tblBorders)
        
        # 设置列宽（适应横向页面）
        widths = [Cm(1.0), Cm(3.0), Cm(2.5), Cm(1.0), Cm(1.5), Cm(1.8), Cm(1.8), Cm(1.8), Cm(1.8), Cm(2.0), Cm(1.5)]
        for i, width in enumerate(widths[:base_cols]):
            for row in table.rows:
                if i < len(row.cells):
                    row.cells[i].width = width
        
        # 设置表头 - 第一行
        header_row1 = table.rows[0]
        if table_type == "guidance_price":
            headers1 = ['序号', '材料名称', '规格型号', '单位', '数量', '送审结算', '', '市场信息价结算', '', '核增（减）额', '权重（%）']
        else:
            headers1 = ['序号', '材料名称', '规格型号', '单位', '数量', '送审结算', '', 'AI 辅助审核', '', '核增（减）额', '权重（%）']
        
        for i, header in enumerate(headers1[:base_cols]):
            if header:  # 跳过空的合并单元格
                cell = header_row1.cells[i]
                cell.text = header
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                
                # 设置表头字体为黑体
                run = cell.paragraphs[0].runs[0]
                run.font.name = 'SimHei'  # 黑体
                run.font.size = Pt(9)
                run.bold = True
        
        # 合并第一行的多级表头
        self._merge_cells_horizontally(table, 0, 5, 6)  # 合并"送审结算"(单价+合价)
        self._merge_cells_horizontally(table, 0, 7, 8)  # 合并"AI辅助审核"或"市场信息价结算"(单价+合价)
        
        # 设置表头 - 第二行
        header_row2 = table.rows[1]
        headers2 = ['', '', '', '', '', '单价', '合价', '单价', '合价', '', '']
        
        for i, header in enumerate(headers2[:base_cols]):
            if header:  # 只设置有内容的单元格
                cell = header_row2.cells[i]
                cell.text = header
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                
                # 设置表头字体为黑体
                run = cell.paragraphs[0].runs[0]
                run.font.name = 'SimHei'  # 黑体
                run.font.size = Pt(8)
                run.bold = True
        
        # 合并第二行不需要子表头的列（将第一行和第二行合并）
        cols_to_merge = [0, 1, 2, 3, 4, 9, 10]  # 序号、材料名称、规格型号、单位、数量、核增减额、权重
        for col_idx in cols_to_merge:
            if col_idx < base_cols:
                try:
                    table.cell(0, col_idx).merge(table.cell(1, col_idx))
                except Exception:
                    pass  # 忽略合并错误
        
        # 添加数据行
        for idx, material in enumerate(materials_data):
            row = table.add_row()
            
            # 填充数据
            data_cells = [
                str(idx + 1),  # 序号
                material.get('materialName', ''),  # 材料名称
                material.get('specification', ''),  # 规格型号
                material.get('unit', ''),  # 单位
                f"{material.get('quantity', 0):,.0f}",  # 数量
                f"{material.get('originalUnitPrice', 0):,.2f}",  # 送审单价
                f"{material.get('originalTotalPrice', 0):,.2f}",  # 送审合价
                f"{material.get('aiUnitPrice', 0):,.2f}",  # AI单价
                f"{material.get('aiTotalPrice', 0):,.2f}",  # AI合价
                f"{material.get('adjustment', 0):+,.2f}",  # 核增减额
                f"{material.get('weightPercentage', 0):.2f}"  # 权重
            ]
            
            for j, data in enumerate(data_cells[:base_cols]):
                cell = row.cells[j]
                cell.text = data
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                
                # 设置字体
                run = cell.paragraphs[0].runs[0]
                run.font.name = 'SimSun'  # 宋体
                run.font.size = Pt(8)
        
        # 添加合计行
        summary_row = table.add_row()
        summary_data = ['', '合计', '', '', '', '', '', '', '', '', '']
        
        # 计算合计
        total_original = sum(m.get('originalTotalPrice', 0) for m in materials_data)
        total_ai = sum(m.get('aiTotalPrice', 0) for m in materials_data)
        total_adjustment = sum(m.get('adjustment', 0) for m in materials_data)
        total_weight = sum(m.get('weightPercentage', 0) for m in materials_data)
        
        summary_data[6] = f"{total_original:,.2f}"  # 送审合价合计
        summary_data[8] = f"{total_ai:,.2f}"  # AI合价合计
        summary_data[9] = f"{total_adjustment:+,.2f}"  # 核增减额合计
        summary_data[10] = f"{total_weight:.2f}"  # 权重合计
        
        for j, data in enumerate(summary_data[:base_cols]):
            cell = summary_row.cells[j]
            cell.text = data
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            
            # 设置字体
            run = cell.paragraphs[0].runs[0]
            run.font.name = 'SimSun'  # 宋体
            run.font.size = Pt(8)
            run.bold = True
        
        # 设置表格边框
        self._set_table_borders(table)
        
        # 添加备注
        notes = doc.add_paragraph()
        if table_type == "analysis":
            notes.text = "备注：（1）本表可扩展；（2）差额为正值即核减，负值即核增；（3）本表可作为过程资料一并归档。"
        else:
            notes.text = "备注：（1）本表可扩展；（2）差额为正值即核减，负值即核增；（3）本表可纳入审价过程资料一并归档。"
        
        notes.runs[0].font.name = 'SimSun'  # 宋体
        notes.runs[0].font.size = Pt(8)
        
        doc.add_paragraph()  # 添加间距
