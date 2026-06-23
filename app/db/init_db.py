from app.db.base import engine, Base
from app.db.models import User, Conversation, Message, Memory, ApprovalQueue, PersonaSettings, Analytics
import asyncio
from sqlalchemy import text

async def init_db():
    async with engine.begin() as conn:
        # Enable pgvector extension (only for PostgreSQL)
        if engine.url.drivername.startswith("postgresql"):
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        # Create tables
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())
