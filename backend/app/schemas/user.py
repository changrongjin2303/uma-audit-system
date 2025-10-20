from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    """用户基础模式"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    full_name: Optional[str] = Field(None, max_length=100, description="真实姓名")
    department: Optional[str] = Field(None, max_length=100, description="部门")
    phone: Optional[str] = Field(None, max_length=20, description="电话号码")


class UserCreate(UserBase):
    """用户创建模式"""
    password: str = Field(..., min_length=8, max_length=128, description="密码")
    role: UserRole = Field(default=UserRole.COST_ENGINEER, description="用户角色")


class UserUpdate(BaseModel):
    """用户更新模式"""
    full_name: Optional[str] = Field(None, max_length=100, description="真实姓名")
    department: Optional[str] = Field(None, max_length=100, description="部门")
    phone: Optional[str] = Field(None, max_length=20, description="电话号码")
    is_active: Optional[bool] = Field(None, description="是否激活")


class UserInDB(UserBase):
    """数据库中的用户模式"""
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    """用户响应模式（不包含敏感信息）"""
    pass


class UserLogin(BaseModel):
    """用户登录模式"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class Token(BaseModel):
    """令牌模式"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """令牌数据模式"""
    username: Optional[str] = None


class PasswordChange(BaseModel):
    """密码修改模式"""
    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., min_length=8, max_length=128, description="新密码")


class PasswordReset(BaseModel):
    """密码重置模式"""
    email: EmailStr = Field(..., description="邮箱地址")


class PasswordResetConfirm(BaseModel):
    """密码重置确认模式"""
    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=8, max_length=128, description="新密码")