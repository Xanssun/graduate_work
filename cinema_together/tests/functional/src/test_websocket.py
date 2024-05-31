import json

import pytest
import websockets

from tests.functional.settings import test_settings


@pytest.mark.asyncio
async def test_websocket():
    token = test_settings.token
    header = {"Authorization": f"Bearer {str(token)}"}
    async with websockets.connect("ws://cinema_together:8005/api/v1/ws/1234-5678-9999-5555", extra_headers=header) as websocket:
        await websocket.send(json.dumps({'msg': 'test_msg'}))
        message = websocket.recv()
        print(message)
        assert message == {'msg': 'test_msg', 'room_id': '1234-5678-9999-5555'}
