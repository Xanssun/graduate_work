from enum import Enum
from typing import Union
from uuid import UUID

from pydantic import BaseModel


class EventType(str, Enum):
    player = 'player'
    chat = 'message'
    error = 'error'


class ActionType(str, Enum):
    stop = 'stop'
    play = 'play'
    skip_forward = 'skip_forward'
    skip_back = 'skip_back'


class BaseEvent(BaseModel):
    type: EventType


class PlayerSchema(BaseEvent):
    user_id: UUID
    is_active: bool
    type: EventType = EventType.player
    action: ActionType
    value: int
    view_progress: int

    class Config:
        arbitrary_types_allowed = True



class ChatSchema(BaseEvent):
    user_id: UUID
    type: EventType = EventType.chat
    message: str


class ErrorSchema(BaseEvent):
    user_id: UUID
    type: EventType = EventType.error
    message: str


def parse_message(json_data: dict) -> Union[PlayerSchema, ChatSchema]:
    type = json_data.get('type')

    if type == EventType.player:
        return PlayerSchema(**json_data)
    elif type == EventType.chat:
        return ChatSchema(**json_data)
    else:
        raise ValueError('Unknown message type')
