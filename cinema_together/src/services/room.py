from fastapi import WebSocket


class Room:
    def __init__(self, room_id):
        self.room = room_id
        self.connections = []

    async def broadcast(self, message):
        for connection in self.connections:
            self._message_processing(message)
            await connection.send_json(message)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)

    def _message_processing(self, message):
        # Здесь должна быть обработка сообщения в зависимости от типа и т.д.
        pass

    @staticmethod
    async def send_message(message: str, websocket: WebSocket):
        await websocket.send_text(message)


rooms = {}
