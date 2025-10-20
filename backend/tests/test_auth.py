import pytest
from httpx import AsyncClient
from tests.conftest import assert_response_success, assert_response_error


class TestAuth:
    """用户认证测试"""
    
    async def test_user_registration_success(self, client: AsyncClient, test_user_data):
        """测试用户注册成功"""
        response = await client.post("/api/v1/auth/register", json=test_user_data)
        assert_response_success(response, 201)
        
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert "password" not in data  # 确保密码不返回
    
    async def test_user_registration_duplicate(self, client: AsyncClient, test_user_data):
        """测试重复用户名注册"""
        # 第一次注册
        response1 = await client.post("/api/v1/auth/register", json=test_user_data)
        assert_response_success(response1, 201)
        
        # 第二次注册相同用户名
        response2 = await client.post("/api/v1/auth/register", json=test_user_data)
        assert_response_error(response2, 400)
        
    async def test_user_registration_invalid_data(self, client: AsyncClient):
        """测试无效数据注册"""
        invalid_data = {
            "username": "",  # 空用户名
            "email": "invalid-email",  # 无效邮箱
            "password": "123"  # 密码太短
        }
        
        response = await client.post("/api/v1/auth/register", json=invalid_data)
        assert_response_error(response, 422)
    
    async def test_user_login_success(self, client: AsyncClient, test_user_data):
        """测试用户登录成功"""
        # 先注册用户
        register_response = await client.post("/api/v1/auth/register", json=test_user_data)
        assert_response_success(register_response, 201)
        
        # 登录
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        response = await client.post("/api/v1/auth/login", data=login_data)
        assert_response_success(response, 200)
        
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    async def test_user_login_invalid_credentials(self, client: AsyncClient):
        """测试无效凭据登录"""
        login_data = {
            "username": "nonexistent_user",
            "password": "wrong_password"
        }
        
        response = await client.post("/api/v1/auth/login", data=login_data)
        assert_response_error(response, 401)
    
    async def test_get_current_user(self, client: AsyncClient, authenticated_headers):
        """测试获取当前用户信息"""
        response = await client.get("/api/v1/auth/me", headers=authenticated_headers)
        assert_response_success(response, 200)
        
        data = response.json()
        assert "username" in data
        assert "email" in data
        assert "role" in data
        assert "password" not in data
    
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """测试未授权获取用户信息"""
        response = await client.get("/api/v1/auth/me")
        assert_response_error(response, 401)
    
    async def test_update_user_profile(self, client: AsyncClient, authenticated_headers):
        """测试更新用户资料"""
        update_data = {
            "full_name": "Updated Name",
            "email": "updated@example.com"
        }
        
        response = await client.put("/api/v1/auth/me", json=update_data, headers=authenticated_headers)
        assert_response_success(response, 200)
        
        data = response.json()
        assert data["full_name"] == update_data["full_name"]
        assert data["email"] == update_data["email"]
    
    async def test_change_password(self, client: AsyncClient, authenticated_headers, test_user_data):
        """测试修改密码"""
        change_data = {
            "old_password": test_user_data["password"],
            "new_password": "new_password_456"
        }
        
        response = await client.post("/api/v1/auth/change-password", json=change_data, headers=authenticated_headers)
        assert_response_success(response, 200)
        
        # 验证新密码可以登录
        login_data = {
            "username": test_user_data["username"],
            "password": change_data["new_password"]
        }
        login_response = await client.post("/api/v1/auth/login", data=login_data)
        assert_response_success(login_response, 200)
    
    async def test_change_password_wrong_old_password(self, client: AsyncClient, authenticated_headers):
        """测试修改密码时旧密码错误"""
        change_data = {
            "old_password": "wrong_old_password",
            "new_password": "new_password_456"
        }
        
        response = await client.post("/api/v1/auth/change-password", json=change_data, headers=authenticated_headers)
        assert_response_error(response, 400)