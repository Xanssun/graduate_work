from contextlib import asynccontextmanager
import logging
from logging import config as logging_config

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text
import uvicorn

from core.config import settings
from core.logger import LOGGING
from db.postgres import async_session
from api.v1 import websocket
from services import listener


@asynccontextmanager
async def lifespan(app: FastAPI):
    listener.global_listener = listener.Listener()
    await listener.global_listener.start_listening()
    logger.info('start Listener')
    yield
    await listener.global_listener.start_listening()
    logger.info('stop Listener')


app = FastAPI(
    title='API кино вместе',
    docs_url='/kino_api/openapi',
    openapi_url='/kino_api/openapi.json',
    default_response_class=JSONResponse,
    lifespan=lifespan
)

logging_config.dictConfig(LOGGING)
logger = logging.getLogger('')


@app.get("/")
async def read_root():
    """Проверка соеденения, тестовая функция"""
    async with async_session() as session:
        try:
            await session.execute(text("SELECT 1"))
            return {"Соединение с базой данных установлено!"}
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": f"Ошибка подключения к базе данных: {str(e)}"})


app.include_router(websocket.router, prefix='/api/v1/ws', tags=['websocket'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.kino_api_host,
        port=settings.kino_api_port,
        reload=True,
    )
