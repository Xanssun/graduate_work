from http import HTTPStatus

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
# from middleware.token import security_access_token
from service.room import RoomService, get_room_service
from shemas.room import (RoomInfoResponseShema, RoomRequestShema,
                         RoomResponseShema)

router = APIRouter()


""" Проверка токена временно закоментированна! """

@router.post(
    '/',
    response_model=RoomResponseShema,
    status_code=HTTPStatus.CREATED,
    summary='Создание комнаты',
    description='Создание комнаты',
)
async def create_room(
    data: RoomRequestShema,
    request: Request,
    # token: dict = Depends(security_access_token),
    room_service: RoomService = Depends(get_room_service)
) -> RoomResponseShema:
    # creator_id = token.get('user_id')
    room = await room_service.create(film_id=data.film_id, creator_id=data.creator_id, users=data.users) # creator_id=creator_id
    return RoomResponseShema(msg='Комната создана', room_id=str(room.id) if room else None)

@router.get(
    '/{room_id}',
    response_model=RoomInfoResponseShema,
    summary='Получение информации о комнате',
    description='Получение информации о комнате',
)
async def get_room_info(
    room_id: str,
    # token: dict = Depends(security_access_token),
    room_service: RoomService = Depends(get_room_service)
) -> RoomInfoResponseShema:
    room_info = await room_service.get(room_id=room_id)
    if not room_info:
        return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={'msg': 'Комната не найдена'})

    return RoomInfoResponseShema(
        id=str(room_info.id),
        film_id=str(room_info.film_id),
        creator_id=str(room_info.creator_id),
        created_at=str(room_info.created_at),
        users=[str(user) for user in room_info.users],
    )