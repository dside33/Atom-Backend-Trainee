from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.cfg import settings


DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session


class Base(DeclarativeBase):
    pass
