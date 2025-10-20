import pytest
from httpx import AsyncClient
from tests.conftest import assert_response_success, assert_response_error


class TestProjects:
    """项目管理测试"""
    
    async def test_create_project_success(self, client: AsyncClient, authenticated_headers, test_project_data):
        """测试创建项目成功"""
        response = await client.post("/api/v1/projects/", json=test_project_data, headers=authenticated_headers)
        assert_response_success(response, 201)
        
        data = response.json()
        assert data["name"] == test_project_data["name"]
        assert data["project_code"] == test_project_data["project_code"]
        assert data["status"] == "draft"
        assert "id" in data
        assert "project_uuid" in data
    
    async def test_create_project_unauthorized(self, client: AsyncClient, test_project_data):
        """测试未授权创建项目"""
        response = await client.post("/api/v1/projects/", json=test_project_data)
        assert_response_error(response, 401)
    
    async def test_create_project_invalid_data(self, client: AsyncClient, authenticated_headers):
        """测试创建项目时数据无效"""
        invalid_data = {
            "name": "",  # 空名称
            "budget": -1000  # 负数预算
        }
        
        response = await client.post("/api/v1/projects/", json=invalid_data, headers=authenticated_headers)
        assert_response_error(response, 422)
    
    async def test_get_projects_list(self, client: AsyncClient, authenticated_headers, test_project_data):
        """测试获取项目列表"""
        # 创建测试项目
        create_response = await client.post("/api/v1/projects/", json=test_project_data, headers=authenticated_headers)
        assert_response_success(create_response, 201)
        
        # 获取项目列表
        response = await client.get("/api/v1/projects/", headers=authenticated_headers)
        assert_response_success(response, 200)
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert len(data["items"]) > 0
        assert data["items"][0]["name"] == test_project_data["name"]
    
    async def test_get_project_detail(self, client: AsyncClient, authenticated_headers, test_project_data):
        """测试获取项目详情"""
        # 创建测试项目
        create_response = await client.post("/api/v1/projects/", json=test_project_data, headers=authenticated_headers)
        assert_response_success(create_response, 201)
        
        project_id = create_response.json()["id"]
        
        # 获取项目详情
        response = await client.get(f"/api/v1/projects/{project_id}", headers=authenticated_headers)
        assert_response_success(response, 200)
        
        data = response.json()
        assert data["name"] == test_project_data["name"]
        assert data["id"] == project_id
    
    async def test_get_project_not_found(self, client: AsyncClient, authenticated_headers):
        """测试获取不存在的项目"""
        response = await client.get("/api/v1/projects/99999", headers=authenticated_headers)
        assert_response_error(response, 404)
    
    async def test_update_project(self, client: AsyncClient, authenticated_headers, test_project_data):
        """测试更新项目"""
        # 创建测试项目
        create_response = await client.post("/api/v1/projects/", json=test_project_data, headers=authenticated_headers)
        assert_response_success(create_response, 201)
        
        project_id = create_response.json()["id"]
        
        # 更新项目
        update_data = {
            "name": "更新后的项目名称",
            "description": "更新后的描述",
            "budget": 2000000.0
        }
        
        response = await client.put(f"/api/v1/projects/{project_id}", json=update_data, headers=authenticated_headers)
        assert_response_success(response, 200)
        
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["budget"] == update_data["budget"]
    
    async def test_delete_project(self, client: AsyncClient, authenticated_headers, test_project_data):
        """测试删除项目"""
        # 创建测试项目
        create_response = await client.post("/api/v1/projects/", json=test_project_data, headers=authenticated_headers)
        assert_response_success(create_response, 201)
        
        project_id = create_response.json()["id"]
        
        # 删除项目
        response = await client.delete(f"/api/v1/projects/{project_id}", headers=authenticated_headers)
        assert_response_success(response, 200)
        
        # 验证项目已删除
        get_response = await client.get(f"/api/v1/projects/{project_id}", headers=authenticated_headers)
        assert_response_error(get_response, 404)
    
    async def test_project_materials_list(self, client: AsyncClient, authenticated_headers, test_project_data):
        """测试获取项目材料列表"""
        # 创建测试项目
        create_response = await client.post("/api/v1/projects/", json=test_project_data, headers=authenticated_headers)
        assert_response_success(create_response, 201)
        
        project_id = create_response.json()["id"]
        
        # 获取项目材料列表
        response = await client.get(f"/api/v1/projects/{project_id}/materials", headers=authenticated_headers)
        assert_response_success(response, 200)
        
        data = response.json()
        assert "items" in data
        assert "total" in data