
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text

# 使用 container host name
DATABASE_URL = "postgresql+asyncpg://postgres:password@uma_audit_postgres_dev:5432/uma_audit"

async def check_data():
    print(f"Connecting to {DATABASE_URL}...")
    engine = create_async_engine(DATABASE_URL)
    async with AsyncSession(engine) as session:
        try:
            # 检查 price_analyses 表（当前分析）
            result = await session.execute(text("SELECT COUNT(*) FROM price_analyses"))
            count_analysis = result.scalar()
            print(f"price_analysis count: {count_analysis}")
            
            # 检查 price_analysis_history 表（历史记录）
            result = await session.execute(text("SELECT COUNT(*) FROM price_analysis_history"))
            count_history = result.scalar()
            print(f"price_analysis_history count: {count_history}")
            
            if count_history > 0:
                # 显示一些历史记录的 material_id
                result = await session.execute(text("SELECT material_id, created_at FROM price_analysis_history ORDER BY created_at DESC LIMIT 5"))
                rows = result.fetchall()
                print("Some history records (material_id, created_at):")
                for row in rows:
                    print(row)
            else:
                print("No history records found.")
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_data())
