import pytest
from httpx import AsyncClient
from tests.conftest import assert_response_success, assert_response_error


class TestBaseMaterials:
    """基准材料管理测试"""
    
    async def test_create_base_material_success(self, client: AsyncClient, authenticated_headers, test_material_data):
        """测试创建基准材料成功"""
        response = await client.post("/api/v1/base-materials/", json=test_material_data, headers=authenticated_headers)
        assert_response_success(response, 201)
        
        data = response.json()
        assert data["name"] == test_material_data["name"]
        assert data["specification"] == test_material_data["specification"]
        assert data["unit"] == test_material_data["unit"]
        assert data["price"] == test_material_data["price"]
        assert "id" in data
    
    async def test_create_base_material_unauthorized(self, client: AsyncClient, test_material_data):
        """测试未授权创建基准材料"""
        response = await client.post("/api/v1/base-materials/", json=test_material_data)
        assert_response_error(response, 401)
    
    async def test_create_base_material_invalid_data(self, client: AsyncClient, authenticated_headers):
        """测试创建基准材料时数据无效"""
        invalid_data = {
            "name": "",  # 空名称
            "price": -100,  # 负价格
            "specification": "test"
        }
        
        response = await client.post("/api/v1/base-materials/", json=invalid_data, headers=authenticated_headers)
        assert_response_error(response, 422)
    
    async def test_get_base_materials_list(self, client: AsyncClient, authenticated_headers, test_material_data):
        """测试获取基准材料列表"""
        # 创建测试材料
        create_response = await client.post("/api/v1/base-materials/", json=test_material_data, headers=authenticated_headers)
        assert_response_success(create_response, 201)
        
        # 获取材料列表
        response = await client.get("/api/v1/base-materials/", headers=authenticated_headers)
        assert_response_success(response, 200)
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert len(data["items"]) > 0
    
    async def test_get_base_materials_with_search(self, client: AsyncClient, authenticated_headers, test_material_data):
        """测试搜索基准材料"""
        # 创建测试材料
        create_response = await client.post("/api/v1/base-materials/", json=test_material_data, headers=authenticated_headers)
        assert_response_success(create_response, 201)
        
        # 搜索材料
        search_params = {"search": "水泥", "category": "建筑材料"}
        response = await client.get("/api/v1/base-materials/", params=search_params, headers=authenticated_headers)
        assert_response_success(response, 200)
        
        data = response.json()
        assert len(data["items"]) > 0
        assert "水泥" in data["items"][0]["name"]
    
    async def test_get_base_material_detail(self, client: AsyncClient, authenticated_headers, test_material_data):
        """测试获取基准材料详情"""
        # 创建测试材料
        create_response = await client.post("/api/v1/base-materials/", json=test_material_data, headers=authenticated_headers)
        assert_response_success(create_response, 201)
        
        material_id = create_response.json()["id"]
        
        # 获取材料详情
        response = await client.get(f"/api/v1/base-materials/{material_id}", headers=authenticated_headers)
        assert_response_success(response, 200)
        
        data = response.json()
        assert data["name"] == test_material_data["name"]
        assert data["id"] == material_id
    
    async def test_update_base_material(self, client: AsyncClient, authenticated_headers, test_material_data):
        """测试更新基准材料"""
        # 创建测试材料
        create_response = await client.post("/api/v1/base-materials/", json=test_material_data, headers=authenticated_headers)
        assert_response_success(create_response, 201)
        
        material_id = create_response.json()["id"]
        
        # 更新材料
        update_data = {
            "name": "更新后的材料",
            "price": 500.0,
            "specification": "更新规格"
        }
        
        response = await client.put(f"/api/v1/base-materials/{material_id}", json=update_data, headers=authenticated_headers)
        assert_response_success(response, 200)
        
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["price"] == update_data["price"]
    
    async def test_delete_base_material(self, client: AsyncClient, authenticated_headers, test_material_data):
        """测试删除基准材料"""
        # 创建测试材料
        create_response = await client.post("/api/v1/base-materials/", json=test_material_data, headers=authenticated_headers)
        assert_response_success(create_response, 201)
        
        material_id = create_response.json()["id"]
        
        # 删除材料
        response = await client.delete(f"/api/v1/base-materials/{material_id}", headers=authenticated_headers)
        assert_response_success(response, 200)
        
        # 验证材料已删除
        get_response = await client.get(f"/api/v1/base-materials/{material_id}", headers=authenticated_headers)
        assert_response_error(get_response, 404)
    
    async def test_batch_operation(self, client: AsyncClient, authenticated_headers, test_material_data):
        """测试批量操作"""
        # 创建多个测试材料
        materials = []
        for i in range(3):
            material_data = test_material_data.copy()
            material_data["name"] = f"测试材料{i+1}"
            material_data["price"] = 100.0 * (i + 1)
            
            create_response = await client.post("/api/v1/base-materials/", json=material_data, headers=authenticated_headers)
            assert_response_success(create_response, 201)
            materials.append(create_response.json()["id"])
        
        # 批量删除
        batch_data = {
            "operation": "delete",
            "material_ids": materials
        }
        
        response = await client.post("/api/v1/base-materials/batch-operation", json=batch_data, headers=authenticated_headers)
        assert_response_success(response, 200)
        
        data = response.json()
        assert data["success_count"] == 3
        assert data["operation"] == "delete"