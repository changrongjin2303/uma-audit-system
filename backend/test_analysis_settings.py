#!/usr/bin/env python3
"""
测试分析设置功能的脚本
"""
import asyncio
import json
from app.core.database import AsyncSessionLocal
from app.models.project import Project
from app.schemas.project import ProjectCreate
from app.services.project import ProjectService
from app.core.simple_auth import SimpleUser

async def test_analysis_settings():
    """测试分析设置功能"""
    async with AsyncSessionLocal() as db:
        # 创建测试用户
        test_user = SimpleUser(user_id=1, username="admin")

        # 创建包含分析设置的项目
        project_data = ProjectCreate(
            name="测试分析设置项目",
            description="这是一个测试分析设置功能的项目",
            project_type="building",
            location="杭州市",
            budget_amount=1000.0,
            base_price_date="2024-12",
            base_price_province="330000",
            base_price_city="330100",
            base_price_district="330106",
            support_price_adjustment=True,
            price_adjustment_range=5.0,
            audit_scope=["price_analysis", "material_matching", "market_comparison"]
        )

        try:
            # 创建项目
            project = await ProjectService.create_project(db, project_data, test_user)
            print(f"✅ 项目创建成功，ID: {project.id}")
            print(f"   项目名称: {project.name}")
            print(f"   基期信息价日期: {project.base_price_date}")
            print(f"   基期信息价省份: {project.base_price_province}")
            print(f"   基期信息价城市: {project.base_price_city}")
            print(f"   基期信息价区县: {project.base_price_district}")
            print(f"   是否支持调价: {project.support_price_adjustment}")
            print(f"   调价范围: {project.price_adjustment_range}%")
            print(f"   分析范围: {project.audit_scope}")

            # 获取项目详情验证数据
            retrieved_project = await ProjectService.get_project_by_id(db, project.id)
            if retrieved_project:
                print(f"✅ 项目详情获取成功")
                print(f"   验证分析设置:")
                print(f"   - 基期信息价日期: {retrieved_project.base_price_date}")
                print(f"   - 基期信息价地区: {retrieved_project.base_price_province} {retrieved_project.base_price_city} {retrieved_project.base_price_district}")
                print(f"   - 调价设置: {retrieved_project.support_price_adjustment} ({retrieved_project.price_adjustment_range}%)")
                print(f"   - 分析范围: {json.dumps(retrieved_project.audit_scope, ensure_ascii=False)}")
            else:
                print("❌ 项目详情获取失败")

        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_analysis_settings())