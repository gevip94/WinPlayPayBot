import asyncio
from database.db import engine, Base
from database import models  # импортируем модели, чтобы они зарегистрировались

async def create_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(create_all())
