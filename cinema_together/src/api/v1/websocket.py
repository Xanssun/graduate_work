import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from service.websocket import Room, rooms

router = APIRouter()
logger = logging.getLogger('')


"""
TO DO
Нужно проверять токен и поправить логирование добавив айди пользователя
"""
@router.websocket('/{room_id}')
async def websocket(websocket: WebSocket, room_id: str):
    await Room.connect(websocket)
    if not (room_obj := rooms.get(room_id)):
        await Room.send_message(f'Room id {room_id} was not found', websocket)
        logger.info(f'Room id {room_id} was not found')
    else:
        room_obj.add_connection(websocket)
        logger.info(f'User connect to room {room_id}')
        try:
            while True:
                data = await websocket.receive_json()
                await room_obj.broadcast(data)
        except WebSocketDisconnect:
            await room_obj.disconnect(websocket)
            logger.info(f'User disconnect from room {room_id}')