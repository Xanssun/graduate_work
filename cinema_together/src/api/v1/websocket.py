import logging

import asyncio
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from middleware.token import security_access_token, Token
from services.websocket import WSManager


router = APIRouter()
logger = logging.getLogger('')


@router.websocket('/{room_id}')
async def websocket(
    websocket: WebSocket,
    room_id: str,
    token: Token = Depends(security_access_token)
):
    q: asyncio.Queue = asyncio.Queue()
    await WSManager.connect(websocket, q, room_id)
    logger.info(f'User {token.user_id} connect to room {room_id}')
    try:
        while True:
            await WSManager.receive_message(room_id, websocket)
            await WSManager.send_message(room_id, websocket, q)
    except WebSocketDisconnect:
        logger.info(f'User {token.user_id} disconnect from room {room_id}')
