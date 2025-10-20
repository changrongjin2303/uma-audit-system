from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User, UserRole

# HTTP Bearer令牌方案
security = HTTPBearer()


async def get_current_user(
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前用户 - 开发模式简化版"""
    # 开发模式：直接返回admin用户，不需要认证
    result = await db.execute(
        select(User).where(User.username == "admin")
    )
    admin_user = result.scalar_one_or_none()
    
    if not admin_user:
        # 创建默认admin用户
        admin_user = User(
            username="admin",
            email="admin@uma-audit.com",
            full_name="系统管理员",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        # 设置默认密码hash
        from app.core.security import get_password_hash
        admin_user.hashed_password = get_password_hash("admin123")
        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)
    
    return admin_user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="用户账户未激活"
        )
    return current_user


def require_roles(*allowed_roles: UserRole):
    """角色权限装饰器"""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足，无法访问此资源"
            )
        return current_user
    return role_checker


# 便捷的权限检查函数
def require_admin():
    """要求管理员权限"""
    return require_roles(UserRole.ADMIN)


def require_auditor():
    """要求审计员权限"""
    return require_roles(UserRole.ADMIN, UserRole.AUDITOR)


def require_cost_engineer():
    """要求造价工程师权限"""
    return require_roles(UserRole.ADMIN, UserRole.AUDITOR, UserRole.COST_ENGINEER)


def require_manager():
    """要求管理员权限"""
    return require_roles(UserRole.ADMIN, UserRole.MANAGER)