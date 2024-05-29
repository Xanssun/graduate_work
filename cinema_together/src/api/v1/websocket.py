import logging

import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from services.websocket import WSManager
from services.listener import global_listener


router = APIRouter()
logger = logging.getLogger('')


"""
TO DO
Нужно проверять токен и поправить логирование добавив айди пользователя
"""
@router.websocket('/{room_id}')
async def websocket(websocket: WebSocket, room_id: str):
    # TO DO Проверка наличия такой комнаты
    q: asyncio.Queue = asyncio.Queue()
    await WSManager.connect(websocket, q, room_id)
    logger.info(f'User connect to room {room_id}')
    try:
        while True:
            await WSManager.receive_message(room_id, websocket)
            await WSManager.send_message(room_id, websocket, q)
    except WebSocketDisconnect:
        logger.info(f'User disconnect from room {room_id}')
