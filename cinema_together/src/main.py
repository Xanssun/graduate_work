from contextlib import asynccontextmanager
import logging
from logging import config as logging_config

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import uvicorn

from core.config import settings
from core.logger import LOGGING
from api.v1 import websocket, room
from db import postgres
from services import listener


logging_config.dictConfig(LOGGING)
logger = logging.getLogger('')


@asynccontextmanager
async def lifespan(app: FastAPI):
    async_engine = create_async_engine(str(settings.kino_sqlalchemy_dsn), echo=True, future=True)
    postgres.async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    listener.global_listener = listener.Listener()
    await listener.global_listener.start_listening()
    logger.info('start database connection')
    logger.info('start listener')
    yield
    await postgres.async_session.close()
    await listener.global_listener.start_listening()
    logger.info('stop database connection')
    logger.info('stop listener')


app = FastAPI(
    title='API кино вместе',
    docs_url='/kino_api/openapi',
    openapi_url='/kino_api/openapi.json',
    default_response_class=HTMLResponse,
    lifespan=lifespan
)


app.include_router(room.router, prefix='/kino_api/v1/cinema', tags=['cinema'])
app.include_router(websocket.router, prefix='/api/v1/ws', tags=['websocket'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.kino_api_host,
        port=settings.kino_api_port,
        reload=True,
    )
