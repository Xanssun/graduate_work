import json
import logging

import aiopg
import asyncio
from asyncio import Queue, Task

from core.config import settings

logger = logging.getLogger('')


class Listener:
    def __init__(self):
        self.subscribers: dict[str, list[Queue]] = {}
        self.listener_task: Task

    async def subscribe(self, room_id: str, q: Queue):
        print('we are subscribed')
        if self.subscribers.get(room_id):
            self.subscribers[room_id].append(q)
        else:
            self.subscribers[room_id] = [q]

    async def start_listening(self):
        self.listener_task = asyncio.create_task(self._listener())

    # Возможно передавать сюда уже коннкшн, а не создавать его внутри
    async def _listener(self) -> None:
        async with aiopg.connect(dsn=str(settings.kino_psql_dsn)) as conn:
            async with conn.cursor() as cur:
                await cur.execute('LISTEN channel')
                while True:
                    message = await conn.notifies.get()
                    message_json = json.loads(message.payload)
                    room_id = message_json.get('room_id')
                    print(self.subscribers)
                    for q in self.subscribers[room_id]:
                        await q.put(message)

    async def stop_listening(self):
        if self.listener_task.done():
            self.listener_task.result()
        else:
            self.listener_task.cancel()


global_listener: Listener | None = None


async def get_listener() -> Listener:
    return global_listener
