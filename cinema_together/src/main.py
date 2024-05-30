from contextlib import asynccontextmanager
import logging
from logging import config as logging_config

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

from core.config import settings
from core.logger import LOGGING
from db.postgres import async_session
from api.v1 import websocket, room
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
    default_response_class=HTMLResponse,
    lifespan=lifespan
)

logging_config.dictConfig(LOGGING)
logger = logging.getLogger('')



app.include_router(room.router, prefix='/kino_api/v1/cinema', tags=['cinema'])
app.include_router(websocket.router, prefix='/api/v1/ws', tags=['websocket'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.kino_api_host,
        port=settings.kino_api_port,
        reload=True,
    )
