import pytest

from app.connections import Connection, ConnectionManager


class TestConnection:
    def test_connection_defaults(self):
        conn = Connection(sid="test-sid")
        assert conn.sid == "test-sid"
        assert conn.client_ip == ""
        assert conn.rooms == set()

    def test_connection_with_ip(self):
        conn = Connection(sid="test-sid", client_ip="192.168.1.1")
        assert conn.sid == "test-sid"
        assert conn.client_ip == "192.168.1.1"


class TestConnectionManager:
    def test_add_connection(self):
        manager = ConnectionManager()
        conn = manager.add("sid-1")
        assert conn.sid == "sid-1"
        assert manager.count() == 1

    def test_add_connection_with_ip(self):
        manager = ConnectionManager()
        conn = manager.add("sid-1", "10.0.0.1")
        assert conn.client_ip == "10.0.0.1"

    def test_remove_connection(self):
        manager = ConnectionManager()
        manager.add("sid-1")
        manager.remove("sid-1")
        assert manager.count() == 0

    def test_remove_nonexistent(self):
        manager = ConnectionManager()
        manager.remove("nonexistent")
        assert manager.count() == 0

    def test_get_connection(self):
        manager = ConnectionManager()
        manager.add("sid-1")
        conn = manager.get("sid-1")
        assert conn is not None
        assert conn.sid == "sid-1"

    def test_get_nonexistent(self):
        manager = ConnectionManager()
        conn = manager.get("nonexistent")
        assert conn is None

    def test_add_room(self):
        manager = ConnectionManager()
        manager.add("sid-1")
        manager.add_room("sid-1", "room-1")
        conn = manager.get("sid-1")
        assert "room-1" in conn.rooms

    def test_add_room_nonexistent_connection(self):
        manager = ConnectionManager()
        manager.add_room("nonexistent", "room-1")
        assert manager.count() == 0

    def test_remove_room(self):
        manager = ConnectionManager()
        manager.add("sid-1")
        manager.add_room("sid-1", "room-1")
        manager.remove_room("sid-1", "room-1")
        conn = manager.get("sid-1")
        assert "room-1" not in conn.rooms

    def test_multiple_rooms(self):
        manager = ConnectionManager()
        manager.add("sid-1")
        manager.add_room("sid-1", "room-1")
        manager.add_room("sid-1", "room-2")
        conn = manager.get("sid-1")
        assert len(conn.rooms) == 2
        assert "room-1" in conn.rooms
        assert "room-2" in conn.rooms

    def test_all_connections(self):
        manager = ConnectionManager()
        manager.add("sid-1")
        manager.add("sid-2")
        manager.add("sid-3")
        all_conns = manager.all()
        assert len(all_conns) == 3
        sids = {c.sid for c in all_conns}
        assert sids == {"sid-1", "sid-2", "sid-3"}

    def test_count(self):
        manager = ConnectionManager()
        assert manager.count() == 0
        manager.add("sid-1")
        assert manager.count() == 1
        manager.add("sid-2")
        assert manager.count() == 2
        manager.remove("sid-1")
        assert manager.count() == 1
