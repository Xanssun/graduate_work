import json
import logging
from asyncio import Queue
from datetime import datetime

import aiopg
from core.config import settings
from db.postgres import get_session
from fastapi import WebSocket
from models.entity import Player, save_message_to_db, save_player_to_db
from service.listener import get_listener
from shemas.msg_player import (ActionType, ChatSchema, PlayerSchema,
                               parse_message)

logger = logging.getLogger('')


class WSManager:

    @staticmethod
    async def connect(websocket: WebSocket, q: Queue, room_id):
        await websocket.accept()
        listener = await get_listener()
        await listener.subscribe(room_id=room_id, q=q)

    @staticmethod
    async def receive_message(room_id, websocket: WebSocket):
        message = await websocket.receive_json()
        message['room_id'] = room_id
        parsed_message = parse_message(message)

        if isinstance(parsed_message, ChatSchema):
            logger.info(
                f"Пользователь {parsed_message.user_id} отправил сообщение {parsed_message.message} в комнате {room_id}"
            )
            # Получаем текущее время
            created_at = datetime.utcnow()

            # Сохранение сообщения в базу данных
            try:
                async for session in get_session():
                    logger.info(f"Сохранение сообщения от пользователя {parsed_message.user_id} в базе данных.")
                    await save_message_to_db(
                        session, parsed_message.user_id, room_id, parsed_message.message, created_at
                    )  # Передача created_at
                    logger.info(f"Сообщение от пользователя {parsed_message.user_id} успешно сохранено в базе данных.")
            except Exception as e:
                logger.error(
                    f"Ошибка при сохранении сообщения от пользователя {parsed_message.user_id} в базе данных: {e}"
                )

            await WSManager.handle_chat_message(parsed_message, room_id, websocket)

        elif isinstance(parsed_message, PlayerSchema):
            new_player = Player()  # Создание нового экземпляра Player
            if parsed_message.action == ActionType.play:
                new_player.is_active = True
            elif parsed_message.action == ActionType.stop:
                new_player.is_active = False
            elif parsed_message.action == ActionType.skip_forward:
                new_player.view_progress += parsed_message.value
            elif parsed_message.action == ActionType.skip_back:
                new_player.view_progress -= parsed_message.value
            else:
                raise ValueError('Unknown message type')

            # Получаем сессию
            async for session in get_session():
                await save_player_to_db(session, new_player.is_active, new_player.view_progress)
            logger.info(
                f"Пользователь {parsed_message.user_id} выполнил действие {parsed_message.action} в комнате {room_id}"
            )
            await WSManager.handle_player_message(parsed_message, room_id, websocket)

    @staticmethod
    async def handle_chat_message(message: ChatSchema, room_id: str, websocket: WebSocket):
        async with aiopg.connect(dsn=str(settings.kino_psql_dsn)) as conn:
            async with conn.cursor() as cur:
                # Преобразуйте UUID в строку перед сериализацией
                message_dict = message.dict()
                message_dict['user_id'] = str(message_dict['user_id'])
                message_data = json.dumps(message_dict)
                await cur.execute("NOTIFY channel, %s", (message_data,))

    @staticmethod
    async def handle_player_message(message: PlayerSchema, room_id: str, websocket: WebSocket):

        async with aiopg.connect(dsn=str(settings.kino_psql_dsn)) as conn:
            async with conn.cursor() as cur:
                # Преобразуйте UUID в строку перед сериализацией
                message_dict = message.dict()
                message_dict['user_id'] = str(message_dict['user_id'])
                message_data = json.dumps(message_dict)
                await cur.execute("NOTIFY channel, %s", (message_data,))

    @staticmethod
    async def send_message(message: str, websocket: WebSocket, q: Queue):
        message_str = await q.get()
        message = json.loads(message_str.payload)
        await websocket.send_json(message)
