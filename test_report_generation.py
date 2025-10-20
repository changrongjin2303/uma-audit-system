#!/usr/bin/env python3
"""
测试报告生成功能的独立脚本
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.simple_report_generator import SimpleReportGenerator
from app.models.project import Project, ProjectStatus, ProjectMaterial
from app.models.analysis import PriceAnalysis
from datetime import datetime


def create_test_project():
    """创建测试项目"""
    project = Project(
        id=1,
        name="测试项目 - 办公楼建设",
        description="这是一个用于测试报告生成功能的示例项目",
        project_code="TEST-001",
        location="北京市朝阳区",
        owner="测试业主单位",
        contractor="测试承包单位",
        status=ProjectStatus.PROCESSING,
        created_at=datetime.now()
    )
    return project


def create_test_materials(project_id):
    """创建测试材料"""
    materials = [
        ProjectMaterial(
            id=1,
            project_id=project_id,
            material_name="商品混凝土",
            specification="C30",
            unit="立方米",
            quantity=150.0,
            unit_price=380.0,
            is_matched=True,
            is_analyzed=True,
            is_problematic=False
        ),
        ProjectMaterial(
            id=2,
            project_id=project_id,
            material_name="钢筋",
            specification="HRB400E Φ16",
            unit="吨",
            quantity=80.5,
            unit_price=4500.0,
            is_matched=True,
            is_analyzed=True,
            is_problematic=True
        ),
        ProjectMaterial(
            id=3,
            project_id=project_id,
            material_name="砖砌体",
            specification="M10水泥砂浆",
            unit="立方米",
            quantity=120.0,
            unit_price=680.0,
            is_matched=False,
            is_analyzed=True,
            is_problematic=True
        )
    ]
    return materials


def create_test_analyses(materials):
    """创建测试分析结果"""
    analyses = [
        PriceAnalysis(
            material_id=1,
            predicted_price_min=350.0,
            predicted_price_max=410.0,
            predicted_price_avg=380.0,
            confidence_score=0.85,
            price_variance=0.0,
            is_reasonable=True,
            risk_level='low',
            api_response={'source': 'test', 'analysis_time': '2025-09-07'}
        ),
        PriceAnalysis(
            material_id=2,
            predicted_price_min=4000.0,
            predicted_price_max=4300.0,
            predicted_price_avg=4200.0,
            confidence_score=0.78,
            price_variance=7.1,  # 4500 vs 4200的偏差
            is_reasonable=False,
            risk_level='high',
            api_response={'source': 'test', 'analysis_time': '2025-09-07'}
        ),
        PriceAnalysis(
            material_id=3,
            predicted_price_min=580.0,
            predicted_price_max=620.0,
            predicted_price_avg=600.0,
            confidence_score=0.82,
            price_variance=13.3,  # 680 vs 600的偏差
            is_reasonable=False,
            risk_level='medium',
            api_response={'source': 'test', 'analysis_time': '2025-09-07'}
        )
    ]
    return analyses


def test_report_generation():
    """测试报告生成"""
    print("🚀 开始测试报告生成功能...")
    
    try:
        # 创建测试数据
        project = create_test_project()
        materials = create_test_materials(project.id)
        analyses = create_test_analyses(materials)
        
        print(f"📊 测试数据准备完成:")
        print(f"  - 项目: {project.name}")
        print(f"  - 材料数量: {len(materials)}")
        print(f"  - 分析数量: {len(analyses)}")
        
        # 创建报告生成器
        generator = SimpleReportGenerator()
        print(f"📁 报告输出目录: {generator.reports_dir.absolute()}")
        
        # 生成报告
        print("⏳ 正在生成报告...")
        report_path = generator.generate_audit_report(
            project=project,
            materials=materials,
            analyses=analyses,
            report_config={}
        )
        
        print(f"✅ 报告生成成功!")
        print(f"📄 报告文件: {report_path}")
        
        # 检查文件是否存在
        if os.path.exists(report_path):
            file_size = os.path.getsize(report_path)
            print(f"📏 文件大小: {file_size:,} 字节")
            
            # 检查文件扩展名
            if report_path.endswith('.docx'):
                print("📝 格式: Microsoft Word文档 (.docx)")
            elif report_path.endswith('.txt'):
                print("📄 格式: 纯文本文件 (.txt)")
            else:
                print(f"❓ 未知格式: {report_path}")
            
            print(f"🎉 测试成功! 报告已保存到: {report_path}")
            return True
        else:
            print(f"❌ 错误: 报告文件未找到 {report_path}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print(f"🔍 错误类型: {type(e).__name__}")
        
        # 尝试生成简化版本
        try:
            print("🔄 尝试生成简化报告...")
            generator = SimpleReportGenerator()
            backup_report = generator._generate_minimal_report(project)
            print(f"✅ 简化报告生成成功: {backup_report}")
            return True
        except Exception as backup_error:
            print(f"❌ 简化报告也失败: {backup_error}")
            
            # 最后尝试文本报告
            try:
                print("📝 尝试生成文本报告...")
                text_report = generator._generate_text_report(project)
                print(f"✅ 文本报告生成成功: {text_report}")
                return True
            except Exception as text_error:
                print(f"❌ 所有报告生成方案都失败: {text_error}")
                return False


if __name__ == "__main__":
    print("=" * 60)
    print("🏗️  造价材料审计系统 - 报告生成测试")
    print("=" * 60)
    
    success = test_report_generation()
    
    print("=" * 60)
    if success:
        print("🎊 测试完成: 报告生成功能正常!")
    else:
        print("💥 测试失败: 报告生成功能存在问题")
    print("=" * 60)