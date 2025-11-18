from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from ..config import settings

engine = create_async_engine(settings.database_url, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    # Import models so metadata includes tables
    from ..models import user, user_api_key  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)