import json

import pytest

from app.connections import manager
from app.dashboard import get_connections_json, get_dashboard_html, get_logs_json
from app.message_log import msg_logger


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


class TestGetDashboardHtmlNewFeatures:
    def test_includes_disconnect_button(self):
        html = get_dashboard_html()
        assert "Disconnect" in html
        assert "disconnectClient" in html

    def test_includes_message_log_tab(self):
        html = get_dashboard_html()
        assert "Message Log" in html
        assert "Message Traffic" in html

    def test_includes_clear_logs_button(self):
        html = get_dashboard_html()
        assert "clearLogs" in html

    def test_includes_websocket_connection(self):
        html = get_dashboard_html()
        assert "admin:connection" in html
        assert "admin:disconnection" in html
        assert "admin:message" in html

    def test_includes_logs_api_endpoint(self):
        html = get_dashboard_html()
        assert "/api/logs" in html

    def test_includes_disconnect_api_endpoint(self):
        html = get_dashboard_html()
        assert "/api/disconnect/" in html


class TestGetLogsJson:
    def test_empty_logs(self):
        msg_logger.clear()
        json_str = get_logs_json()
        data = json.loads(json_str)
        assert data["count"] == 0
        assert data["logs"] == []

    def test_single_log(self):
        msg_logger.clear()
        msg_logger.log(event="message", from_sid="sid-1", data={"text": "hello"})
        json_str = get_logs_json()
        data = json.loads(json_str)
        assert data["count"] == 1
        log = data["logs"][0]
        assert log["event"] == "message"
        assert log["from"] == "sid-1"
        assert log["data"] == {"text": "hello"}
        assert "timestamp" in log
        msg_logger.clear()

    def test_multiple_logs(self):
        msg_logger.clear()
        msg_logger.log(event="message", from_sid="sid-1")
        msg_logger.log(event="join_room", from_sid="sid-2", to_room="general")
        json_str = get_logs_json()
        data = json.loads(json_str)
        assert data["count"] == 2
        events = {l["event"] for l in data["logs"]}
        assert events == {"message", "join_room"}
        msg_logger.clear()

    def test_room_in_log(self):
        msg_logger.clear()
        msg_logger.log(event="room_message", from_sid="sid-1", to_room="chat", data="hello")
        json_str = get_logs_json()
        data = json.loads(json_str)
        log = data["logs"][0]
        assert log["room"] == "chat"
        msg_logger.clear()
