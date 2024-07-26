
from src.database.session_database import engine
import asyncio

from sqlalchemy import text

async def run():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT version();"))
        print(res.all())

asyncio.run(run())