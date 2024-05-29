from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_websocket():
    with TestClient(app) as client:
        with client.websocket_connect("/api/v1/ws/1234-5678-9999-5555") as websocket:
            websocket.send_json({'msg': 'test_msg'})
            data = websocket.receive_json()
            assert data == {'msg': 'test_msg', 'room_id': '1234-5678-9999-5555'}
