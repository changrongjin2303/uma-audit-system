import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from tests.conftest import assert_response_success, assert_response_error


class TestPriceAnalysis:
    """价格分析测试"""
    
    @pytest.fixture
    async def test_project_with_materials(self, client: AsyncClient, authenticated_headers, test_project_data):
        """创建包含材料的测试项目"""
        # 创建项目
        project_response = await client.post("/api/v1/projects/", json=test_project_data, headers=authenticated_headers)
        assert_response_success(project_response, 201)
        
        project_id = project_response.json()["id"]
        
        # 模拟上传Excel并导入材料
        materials_data = [
            {
                "name": "无信息价材料1",
                "specification": "规格1",
                "unit": "m³",
                "quantity": 100.0,
                "unit_price": 200.0,
                "total_price": 20000.0
            },
            {
                "name": "无信息价材料2", 
                "specification": "规格2",
                "unit": "kg",
                "quantity": 500.0,
                "unit_price": 50.0,
                "total_price": 25000.0
            }
        ]
        
        # 导入材料数据
        import_data = {
            "materials": materials_data,
            "column_mapping": {
                "name": "材料名称",
                "specification": "规格",
                "unit": "单位",
                "quantity": "数量",
                "unit_price": "单价",
                "total_price": "合价"
            }
        }
        
        import_response = await client.post(
            f"/api/v1/projects/{project_id}/import-materials",
            json=import_data,
            headers=authenticated_headers
        )
        assert_response_success(import_response, 201)
        
        return project_id
    
    @patch('app.services.ai_analysis.AIAnalysisService.analyze_material_price')
    async def test_analyze_project_materials_success(self, mock_ai_analyze, client: AsyncClient, 
                                                   authenticated_headers, test_project_with_materials):
        """测试项目材料分析成功"""
        project_id = await test_project_with_materials
        
        # 模拟AI分析结果
        mock_ai_analyze.return_value = {
            "predicted_price_min": 180.0,
            "predicted_price_max": 220.0,
            "predicted_price_avg": 200.0,
            "confidence_score": 0.85,
            "data_sources": [{"name": "test_source", "price": 200.0}],
            "reasoning": "基于市场数据分析",
            "risk_factors": ["价格波动"],
            "recommendations": ["建议采用区间定价"]
        }
        
        # 执行批量分析
        response = await client.post(f"/api/v1/analysis/{project_id}/analyze", headers=authenticated_headers)
        assert_response_success(response, 200)
        
        data = response.json()
        assert "analysis_id" in data
        assert data["status"] == "started"
        assert data["total_materials"] > 0
    
    async def test_analyze_project_unauthorized(self, client: AsyncClient, test_project_with_materials):
        """测试未授权分析项目"""
        project_id = await test_project_with_materials
        
        response = await client.post(f"/api/v1/analysis/{project_id}/analyze")
        assert_response_error(response, 401)
    
    async def test_analyze_nonexistent_project(self, client: AsyncClient, authenticated_headers):
        """测试分析不存在的项目"""
        response = await client.post("/api/v1/analysis/99999/analyze", headers=authenticated_headers)
        assert_response_error(response, 404)
    
    @patch('app.services.ai_analysis.AIAnalysisService.analyze_material_price')
    async def test_analyze_single_material(self, mock_ai_analyze, client: AsyncClient, 
                                         authenticated_headers, test_project_with_materials):
        """测试单个材料分析"""
        project_id = await test_project_with_materials
        
        # 获取项目材料
        materials_response = await client.get(f"/api/v1/projects/{project_id}/materials", headers=authenticated_headers)
        assert_response_success(materials_response, 200)
        
        materials = materials_response.json()["items"]
        material_id = materials[0]["id"]
        
        # 模拟AI分析结果
        mock_ai_analyze.return_value = {
            "predicted_price_min": 180.0,
            "predicted_price_max": 220.0,
            "predicted_price_avg": 200.0,
            "confidence_score": 0.85,
            "data_sources": [{"name": "test_source", "price": 200.0}],
            "reasoning": "基于市场数据分析",
            "risk_factors": ["价格波动"],
            "recommendations": ["建议采用区间定价"]
        }
        
        # 分析单个材料
        response = await client.post(f"/api/v1/analysis/materials/{material_id}/analyze", headers=authenticated_headers)
        assert_response_success(response, 200)
        
        data = response.json()
        assert data["material_id"] == material_id
        assert "predicted_price_min" in data
        assert "predicted_price_max" in data
        assert "confidence_score" in data
    
    async def test_get_analysis_results(self, client: AsyncClient, authenticated_headers, test_project_with_materials):
        """测试获取分析结果"""
        project_id = await test_project_with_materials
        
        response = await client.get(f"/api/v1/analysis/{project_id}/analysis-results", headers=authenticated_headers)
        assert_response_success(response, 200)
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "statistics" in data
    
    async def test_get_analysis_statistics(self, client: AsyncClient, authenticated_headers, test_project_with_materials):
        """测试获取分析统计"""
        project_id = await test_project_with_materials
        
        response = await client.get(f"/api/v1/analysis/{project_id}/analysis-statistics", headers=authenticated_headers)
        assert_response_success(response, 200)
        
        data = response.json()
        assert "total_materials" in data
        assert "analyzed_materials" in data
        assert "pending_materials" in data
        assert "success_rate" in data
    
    async def test_get_available_ai_services(self, client: AsyncClient, authenticated_headers):
        """测试获取可用AI服务"""
        response = await client.get("/api/v1/analysis/ai-services/available", headers=authenticated_headers)
        assert_response_success(response, 200)
        
        data = response.json()
        assert "services" in data
        assert isinstance(data["services"], list)
    
    @patch('app.services.ai_analysis.AIAnalysisService.test_service')
    async def test_test_ai_service(self, mock_test_service, client: AsyncClient, authenticated_headers):
        """测试AI服务可用性"""
        mock_test_service.return_value = {"status": "available", "response_time": 0.5}
        
        test_data = {
            "service": "openai",
            "test_prompt": "测试提示"
        }
        
        response = await client.post("/api/v1/analysis/ai-services/test", json=test_data, headers=authenticated_headers)
        assert_response_success(response, 200)
        
        data = response.json()
        assert data["service"] == "openai"
        assert "status" in data
        assert "response_time" in data
    
    async def test_get_material_analysis(self, client: AsyncClient, authenticated_headers, test_project_with_materials):
        """测试获取单个材料分析结果"""
        project_id = await test_project_with_materials
        
        # 获取项目材料
        materials_response = await client.get(f"/api/v1/projects/{project_id}/materials", headers=authenticated_headers)
        assert_response_success(materials_response, 200)
        
        materials = materials_response.json()["items"]
        material_id = materials[0]["id"]
        
        response = await client.get(f"/api/v1/analysis/materials/{material_id}/analysis", headers=authenticated_headers)
        # 由于还没有分析结果，可能返回404或空结果
        assert response.status_code in [200, 404]