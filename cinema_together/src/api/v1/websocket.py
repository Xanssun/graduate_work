import asyncio
import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from middleware.token import security_access_token
from service.websocket import WSManager

router = APIRouter()
logger = logging.getLogger('')

@router.websocket('/{room_id}')
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    token: str = Query(None)
):
    # Обработка токена из параметра запроса
    decoded_token = security_access_token._parse_token(token)
    if not decoded_token or decoded_token.is_expired():
        await websocket.close(code=1008)  # 1008: Policy Violation
        return

    q: asyncio.Queue = asyncio.Queue()
    await WSManager.connect(websocket, q, room_id)
    logger.info(f'Пользователь {decoded_token.user_id} подключился к комнате {room_id}')
    try:
        while True:
            await WSManager.receive_message(room_id, websocket)
            await WSManager.send_message(room_id, websocket, q)
    except WebSocketDisconnect:
        logger.info(f'Пользователь {decoded_token.user_id} отключился от комнаты {room_id}')

