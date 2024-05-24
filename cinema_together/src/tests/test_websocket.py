from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_websocket():
    client = TestClient(app)
    with client.websocket_connect("/api/v1/ws/1234-5678-9999-5555") as websocket:
        data = websocket.receive_text()
        assert data == 'Room id 1234-5678-9999-5555 was not found'
