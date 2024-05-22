from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from services.room import rooms, Room


router = APIRouter()


"""
TO DO
Нужно проверять токен и возможно
при дисконнете отсылать сообщение что такой то пользователь покинул чат.
Добавить логгинг и уведомления о подключении - отключении пользователя
Нужно ли удалять комнату, если там не осталось пользователей или какой-нибудь таймаут на их
существование?
"""
@router.websocket('/{room_id}')
async def websocket(websocket: WebSocket, room_id: str):
    if not (room_obj := rooms.get(room_id)):
        Room.send_message(f'Room id {room_id} was not found', websocket)
    else:
        await room_obj.connect(websocket)
        try:
            while True:
                data = await websocket.receive_json()
                await room_obj.broadcast(data)
        except WebSocketDisconnect:
            await room_obj.disconnect(websocket)
