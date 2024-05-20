from core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


dsn = f'postgresql+asyncpg://{settings.kino_db_user}:\
    {settings.kino_db_password}@{settings.kino_db_host}:\
    {settings.kino_db_port}/{settings.kino_db_name}'

async_engine = create_async_engine(dsn, echo=True, future=True)
async_session = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)
