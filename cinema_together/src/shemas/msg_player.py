from enum import Enum

from .base import OrjsonBaseModel


class AventType(str, Enum):
    player = 'player'
    chat = 'message'
    error = 'error'


class ActionType(str, Enum):
    stop = 'stop'
    play = 'play'
    skip_forward = 'skip_forward'
    skip_back = 'skip_back'


class BaseAvent(OrjsonBaseModel):
    type: AventType


class Player(BaseAvent):
    type: AventType = AventType.player
    action: ActionType


class Chat(BaseAvent):
    type: AventType = AventType.chat
    message: str
