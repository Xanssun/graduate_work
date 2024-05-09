from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from core.settings import settings

# Создаём базовый класс для будущих моделей
Base = declarative_base()


dsn = f'postgresql+asyncpg://{settings.auth_db_user}:\
    {settings.auth_db_password}@{settings.auth_db_host}:\
    {settings.auth_db_port}/{settings.auth_db_name}'

async_engine = create_async_engine(dsn, echo=True, future=True)
async_session = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


# Функция понадобится при внедрении зависимостей
# Dependency
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def purge_database() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
