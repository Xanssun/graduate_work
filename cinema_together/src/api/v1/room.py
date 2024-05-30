from http import HTTPStatus

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from middleware.token import Token, security_access_token
from service.room import RoomService, get_room_service
from shemas.room import (RoomInfoResponseShema, RoomRequestShema,
                         RoomResponseShema)

router = APIRouter()

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
    token: Token = Depends(security_access_token),
    room_service: RoomService = Depends(get_room_service)
) -> JSONResponse:
    creator_id = token.user_id
    room = await room_service.create(film_id=data.film_id, creator_id=creator_id, users=data.users)
    response_data = {
        'msg': 'Комната создана',
        'room_id': str(room.id) if room else None
    }
    return JSONResponse(content=response_data, status_code=HTTPStatus.CREATED)


@router.get(
    '/{room_id}',
    response_model=RoomInfoResponseShema,
    summary='Получение информации о комнате',
    description='Получение информации о комнате',
)
async def get_room_info(
    room_id: str,
    token: Token = Depends(security_access_token),
    room_service: RoomService = Depends(get_room_service)
) -> JSONResponse:
    room_info = await room_service.get(room_id=room_id)
    if not room_info:
        return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={'msg': 'Комната не найдена'})

    response_data = {
        'room_id': str(room_info.id),
        'film_id': str(room_info.film_id),
        'creator_id': str(room_info.creator_id),
        'created_at': str(room_info.created_at),
    }
    return JSONResponse(content=response_data)


@router.post(
    '/{room_id}/complete',
    response_model=RoomResponseShema,
    status_code=HTTPStatus.OK,
    summary='Завершить комнату',
    description='Завершить комнату',
)
async def complete_room(
    room_id: str,
    request: Request,
    token: Token = Depends(security_access_token),
    room_service: RoomService = Depends(get_room_service)
) -> JSONResponse:
    creator_id = token.user_id
    room = await room_service.complete(room_id=room_id, creator_id=creator_id)
    response_data = {
        'msg': 'Комната завершена',
        'room_id': str(room.id)
    }
    return JSONResponse(content=response_data)
