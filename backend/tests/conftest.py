import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
from app.core.config import Settings
from main import create_app


# 测试配置
class TestSettings(Settings):
    """测试环境配置"""
    DEBUG = True
    DATABASE_URL = "sqlite+aiosqlite:///./test.db"
    REDIS_URL = "redis://localhost:6379/15"  # 使用不同的Redis数据库
    SECRET_KEY = "test-secret-key-for-testing-only"
    LOG_LEVEL = "DEBUG"


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db():
    """创建测试数据库"""
    # 创建测试数据库引擎
    engine = create_async_engine("sqlite+aiosqlite:///./test.db", echo=False)
    
    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # 清理测试数据库
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_db) -> AsyncSession:
    """创建数据库会话"""
    async_session = sessionmaker(
        test_db, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """创建测试客户端"""
    app = create_app()
    
    # 覆盖数据库依赖
    async def get_test_db():
        yield db_session
    
    app.dependency_overrides[get_db] = get_test_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def sync_client() -> TestClient:
    """创建同步测试客户端"""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def test_user_data():
    """测试用户数据"""
    return {
        "username": "test_user",
        "email": "test@example.com",
        "password": "test_password_123",
        "full_name": "Test User",
        "role": "造价工程师"
    }


@pytest.fixture
def test_project_data():
    """测试项目数据"""
    return {
        "name": "测试项目",
        "description": "这是一个测试项目",
        "project_code": "TEST001",
        "location": "北京市",
        "budget": 1000000.0,
        "client": "测试客户"
    }


@pytest.fixture
def test_material_data():
    """测试材料数据"""
    return {
        "name": "水泥",
        "specification": "P.O 42.5",
        "unit": "t",
        "category": "建筑材料",
        "region": "北京",
        "price": 450.0,
        "source": "政府信息价",
        "effective_date": "2024-01-01"
    }


@pytest.fixture
async def authenticated_headers(client: AsyncClient, test_user_data):
    """获取认证头信息"""
    # 创建测试用户
    register_response = await client.post("/api/v1/auth/register", json=test_user_data)
    assert register_response.status_code == 201
    
    # 登录获取token
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    login_response = await client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == 200
    
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# 测试工具函数
def assert_response_success(response, expected_status=200):
    """断言响应成功"""
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}: {response.text}"


def assert_response_error(response, expected_status=400):
    """断言响应错误"""
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}: {response.text}"
    assert "error" in response.json() or "detail" in response.json()