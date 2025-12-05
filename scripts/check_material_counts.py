import asyncio
from sqlalchemy import select, func, and_
from app.core.database import AsyncSessionLocal
from app.models.material import BaseMaterial

async def check_materials():
    async with AsyncSessionLocal() as db:
        stmt = select(
            BaseMaterial.price_date,
            BaseMaterial.price_type,
            BaseMaterial.region,
            BaseMaterial.province,
            BaseMaterial.city,
            func.count(BaseMaterial.id).label('count')
        ).group_by(
            BaseMaterial.price_date,
            BaseMaterial.price_type,
            BaseMaterial.region,
            BaseMaterial.province,
            BaseMaterial.city
        ).order_by(
            BaseMaterial.price_date.desc(),
            BaseMaterial.region
        )
        
        result = await db.execute(stmt)
        rows = result.all()
        
        print(f"{'Price Date':<15} | {'Type':<12} | {'Region':<15} | {'Province':<10} | {'City':<10} | {'Count':<5}")
        print("-" * 80)
        for row in rows:
            print(f"{str(row.price_date):<15} | {str(row.price_type):<12} | {str(row.region):<15} | {str(row.province):<10} | {str(row.city):<10} | {row.count:<5}")

        total_stmt = select(func.count(BaseMaterial.id))
        total = await db.scalar(total_stmt)
        print("-" * 80)
        print(f"Total materials: {total}")

if __name__ == "__main__":
    asyncio.run(check_materials())

