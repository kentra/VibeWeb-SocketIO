import json

import pytest

from app.connections import manager
from app.dashboard import get_connections_json, get_dashboard_html


class TestGetDashboardHtml:
    def test_returns_html(self):
        html = get_dashboard_html()
        assert "<!DOCTYPE html>" in html
        assert "VibeWeb SocketIO Dashboard" in html

    def test_includes_api_endpoint(self):
        html = get_dashboard_html()
        assert "/api/connections" in html

    def test_includes_table_headers(self):
        html = get_dashboard_html()
        assert "Session ID" in html
        assert "Client IP" in html
        assert "Connected At" in html
        assert "Rooms" in html


class TestGetConnectionsJson:
    def test_empty_connections(self):
        manager._connections.clear()
        json_str = get_connections_json()
        data = json.loads(json_str)
        assert data["count"] == 0
        assert data["connections"] == []

    def test_single_connection(self):
        manager._connections.clear()
        manager.add("test-sid", "192.168.1.1")
        json_str = get_connections_json()
        data = json.loads(json_str)
        assert data["count"] == 1
        assert len(data["connections"]) == 1
        conn = data["connections"][0]
        assert conn["sid"] == "test-sid"
        assert conn["client_ip"] == "192.168.1.1"
        assert conn["rooms"] == []
        assert "connected_at" in conn
        manager._connections.clear()

    def test_multiple_connections(self):
        manager._connections.clear()
        manager.add("sid-1", "10.0.0.1")
        manager.add("sid-2", "10.0.0.2")
        manager.add_room("sid-1", "room-1")
        json_str = get_connections_json()
        data = json.loads(json_str)
        assert data["count"] == 2
        sids = {c["sid"] for c in data["connections"]}
        assert sids == {"sid-1", "sid-2"}
        manager._connections.clear()

    def test_includes_rooms(self):
        manager._connections.clear()
        manager.add("sid-1")
        manager.add_room("sid-1", "general")
        manager.add_room("sid-1", "chat")
        json_str = get_connections_json()
        data = json.loads(json_str)
        conn = data["connections"][0]
        assert set(conn["rooms"]) == {"general", "chat"}
        manager._connections.clear()
