import json
import logging

import aiopg
from asyncio import Queue
from fastapi import WebSocket

from core.config import settings
from services.listener import get_listener

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
        async with aiopg.connect(dsn=str(settings.kino_psql_dsn)) as conn:
            async with conn.cursor() as cur:
                # TO DO Коннектимся, преобразовываем, пишем в базу, что нам надо и шлём после этого нотифай.
                message = json.dumps(message)
                await cur.execute("NOTIFY channel, %s", (message,))

    @staticmethod
    def _message_processing(message):
        # Здесь должна быть обработка сообщения в зависимости от типа и т.д.
        pass

    @staticmethod
    async def send_message(message: str, websocket: WebSocket, q: Queue):
        message_str = await q.get()
        message = json.loads(message_str.payload)
        await websocket.send_json(message)
