from typing import Optional
from uuid import UUID

from .base import OrjsonBaseModel


class RoomRequestShema(OrjsonBaseModel):
    film_id: UUID
    creator_id: UUID  # Предполагаем, что creator_id передается с фронта
    users: list[UUID]


class RoomResponseShema(OrjsonBaseModel):
    msg: str
    room_id: Optional[str]


class RoomInfoResponseShema(OrjsonBaseModel):
    """Модель для инфо о комнате"""
    id: str
    film_id: str
    creator_id: str
    created_at: str
    users: list[str]
