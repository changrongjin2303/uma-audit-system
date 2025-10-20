from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func
from sqlalchemy.orm import selectinload

from app.models.user import User, UserSession, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password, generate_session_token
from app.core.config import settings


class UserService:
    """用户服务类"""
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """创建用户"""
        # 检查用户名和邮箱是否已存在
        stmt = select(User).where(
            or_(User.username == user_data.username, User.email == user_data.email)
        )
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            if existing_user.username == user_data.username:
                raise ValueError("用户名已存在")
            if existing_user.email == user_data.email:
                raise ValueError("邮箱已存在")
        
        # 创建新用户
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role,
            department=user_data.department,
            phone=user_data.phone,
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def authenticate_user(
        db: AsyncSession, 
        username_or_email: str, 
        password: str
    ) -> Optional[User]:
        """用户认证"""
        # 查找用户（支持用户名或邮箱登录）
        stmt = select(User).where(
            or_(User.username == username_or_email, User.email == username_or_email)
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(password, user.hashed_password):
            return None
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        await db.commit()
        
        return user
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_user(
        db: AsyncSession, 
        user: User, 
        user_data: UserUpdate
    ) -> User:
        """更新用户信息"""
        update_data = user_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def change_password(
        db: AsyncSession, 
        user: User, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """修改密码"""
        if not verify_password(current_password, user.hashed_password):
            return False
        
        user.hashed_password = get_password_hash(new_password)
        await db.commit()
        return True
    
    @staticmethod
    async def deactivate_user(db: AsyncSession, user: User) -> User:
        """停用用户"""
        user.is_active = False
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def activate_user(db: AsyncSession, user: User) -> User:
        """激活用户"""
        user.is_active = True
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def get_users(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[User]:
        """获取用户列表"""
        stmt = select(User)
        
        # 过滤条件
        if role:
            stmt = stmt.where(User.role == role)
        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)
        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(
                or_(
                    User.username.ilike(search_term),
                    User.full_name.ilike(search_term),
                    User.email.ilike(search_term)
                )
            )
        
        stmt = stmt.offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_users_count(
        db: AsyncSession,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> int:
        """获取用户总数"""
        stmt = select(func.count(User.id))
        
        # 过滤条件
        if role:
            stmt = stmt.where(User.role == role)
        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)
        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(
                or_(
                    User.username.ilike(search_term),
                    User.full_name.ilike(search_term),
                    User.email.ilike(search_term)
                )
            )
        
        result = await db.execute(stmt)
        return result.scalar() or 0