#!/usr/bin/env python3
"""
创建默认管理员账号脚本
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal, create_tables
from app.models.user import User, UserRole
from app.core.security import get_password_hash


async def create_admin_user():
    """创建默认管理员账号"""
    
    # 确保表已创建
    await create_tables()
    
    async with AsyncSessionLocal() as session:
        try:
            # 检查是否已存在管理员账号
            result = await session.execute(
                select(User).where(User.username == "admin")
            )
            existing_admin = result.scalar_one_or_none()
            
            if existing_admin:
                print("✅ 管理员账号已存在")
                print(f"   用户名: {existing_admin.username}")
                print(f"   邮箱: {existing_admin.email}")
                return
            
            # 创建管理员账号
            admin_user = User(
                username="admin",
                email="admin@uma-audit.com",
                full_name="系统管理员",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True
            )
            
            session.add(admin_user)
            await session.commit()
            
            print("🎉 默认管理员账号创建成功！")
            print("="*50)
            print("📋 登录信息：")
            print(f"   用户名: admin")
            print(f"   密码: admin123")
            print(f"   邮箱: admin@uma-audit.com")
            print(f"   角色: 系统管理员")
            print("="*50)
            print("💡 请登录后及时修改密码！")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ 创建管理员账号失败: {str(e)}")
            raise


if __name__ == "__main__":
    from sqlalchemy import select
    asyncio.run(create_admin_user())