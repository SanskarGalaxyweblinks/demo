from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from ..config import settings

# Create Async Engine
engine = create_async_engine(settings.database_url, echo=True)

# Create Session Local
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

Base = declarative_base()

# Dependency for routes to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Initializer to create tables (for dev only; use Alembic for production)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)