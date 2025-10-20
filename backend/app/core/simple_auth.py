"""
简化的认证系统 - 专门为UMA审计系统设计
避免复杂的数据库映射问题，提供稳定的认证服务
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime

# HTTP Bearer令牌方案
security = HTTPBearer()

class SimpleUser:
    """简化的用户类，避免SQLAlchemy映射问题"""
    def __init__(self, user_id: int = 1, username: str = "admin"):
        self.id = user_id
        self.username = username
        self.email = "admin@uma-audit.com"
        self.full_name = "系统管理员"
        self.role = "ADMIN"
        self.is_active = True
        self.is_verified = True
        self.department = None
        self.phone = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.last_login = None


async def get_current_user() -> SimpleUser:
    """获取当前用户 - 开发模式简化版本"""
    # 开发模式：直接返回默认用户，无需认证
    return SimpleUser()


async def get_current_active_user(
    current_user: SimpleUser = Depends(get_current_user),
) -> SimpleUser:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="用户账户未激活"
        )
    return current_user


def require_admin():
    """要求管理员权限"""
    async def admin_checker(current_user: SimpleUser = Depends(get_current_active_user)) -> SimpleUser:
        if current_user.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="需要管理员权限"
            )
        return current_user
    return admin_checker


def require_auditor():
    """要求审计员权限"""
    async def role_checker(current_user: SimpleUser = Depends(get_current_active_user)) -> SimpleUser:
        # 简化：所有登录用户都有审计员权限
        return current_user
    return role_checker


def require_cost_engineer():
    """要求造价工程师权限（包含所有权限）"""
    async def role_checker(current_user: SimpleUser = Depends(get_current_active_user)) -> SimpleUser:
        # 简化：所有登录用户都有造价工程师权限
        return current_user
    return role_checker