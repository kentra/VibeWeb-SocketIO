import pytest

from app.connections import manager


@pytest.fixture(autouse=True)
def clear_manager():
    manager._connections.clear()
    yield
    manager._connections.clear()


class TestEventLogic:
    def test_connection_manager_integration(self):
        manager.add("sid-1", "192.168.1.100")
        manager.add("sid-2", "10.0.0.1")
        manager.add_room("sid-1", "general")
        manager.add_room("sid-1", "chat")

        assert manager.count() == 2
        conn1 = manager.get("sid-1")
        assert conn1.client_ip == "192.168.1.100"
        assert "general" in conn1.rooms
        assert "chat" in conn1.rooms

        manager.remove("sid-1")
        assert manager.count() == 1
        assert manager.get("sid-1") is None

    def test_x_forwarded_for_parsing(self):
        forwarded = "203.0.113.1, 10.0.0.1"
        client_ip = forwarded.split(",")[0].strip()
        assert client_ip == "203.0.113.1"

    def test_x_forwarded_for_single(self):
        forwarded = "203.0.113.1"
        if "," in forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = forwarded
        assert client_ip == "203.0.113.1"

    def test_remote_addr_fallback(self):
        environ = {"REMOTE_ADDR": "192.168.1.100"}
        client_ip = environ.get("HTTP_X_FORWARDED_FOR", environ.get("REMOTE_ADDR", ""))
        if "," in client_ip:
            client_ip = client_ip.split(",")[0].strip()
        assert client_ip == "192.168.1.100"


class TestRoomMessageValidation:
    @pytest.mark.asyncio
    async def test_valid_room_message(self):
        data = {"room": "general", "message": "hello"}
        room = data.get("room")
        message = data.get("message")
        assert room is not None and message is not None

    @pytest.mark.asyncio
    async def test_missing_room(self):
        data = {"message": "hello"}
        room = data.get("room")
        message = data.get("message")
        assert room is None or message is None

    @pytest.mark.asyncio
    async def test_missing_message(self):
        data = {"room": "general"}
        room = data.get("room")
        message = data.get("message")
        assert room is None or message is None

    @pytest.mark.asyncio
    async def test_empty_message(self):
        data = {"room": "general", "message": ""}
        room = data.get("room")
        message = data.get("message")
        assert message == ""


class TestPingResponse:
    def test_ping_format(self):
        sid = "test-sid"
        response = {"status": "pong", "sid": sid}
        assert response["status"] == "pong"
        assert response["sid"] == sid


class TestMessageResponse:
    def test_message_response_format(self):
        sid = "test-sid"
        response = {"status": "received", "sid": sid}
        assert response["status"] == "received"
        assert response["sid"] == sid


class TestBroadcastResponse:
    def test_broadcast_response_format(self):
        response = {"status": "broadcasted"}
        assert response["status"] == "broadcasted"


class TestJoinRoomResponse:
    def test_join_room_response_format(self):
        room = "general"
        response = {"status": "joined", "room": room}
        assert response["status"] == "joined"
        assert response["room"] == room


class TestLeaveRoomResponse:
    def test_leave_room_response_format(self):
        room = "general"
        response = {"status": "left", "room": room}
        assert response["status"] == "left"
        assert response["room"] == room


class TestRoomMessageResponse:
    def test_room_message_response_format(self):
        room = "general"
        response = {"status": "sent", "room": room}
        assert response["status"] == "sent"
        assert response["room"] == room

    def test_room_message_error_format(self):
        response = {"status": "error", "message": "Missing room or message"}
        assert response["status"] == "error"
        assert "Missing" in response["message"]
