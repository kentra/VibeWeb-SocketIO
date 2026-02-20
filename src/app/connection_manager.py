from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Connection:
    sid: str
    connected_at: datetime = field(default_factory=datetime.utcnow)
    session_data: dict[str, Any] = field(default_factory=dict)
    rooms: set[str] = field(default_factory=set)
    client_info: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sid": self.sid,
            "connected_at": self.connected_at.isoformat(),
            "session_data": self.session_data,
            "rooms": list(self.rooms),
            "client_info": self.client_info,
        }


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, Connection] = {}

    def add_connection(self, sid: str, client_info: dict[str, Any] | None = None) -> Connection:
        conn = Connection(
            sid=sid,
            client_info=client_info or {},
        )
        self._connections[sid] = conn
        return conn

    def remove_connection(self, sid: str) -> Connection | None:
        return self._connections.pop(sid, None)

    def get_connection(self, sid: str) -> Connection | None:
        return self._connections.get(sid)

    def update_session(self, sid: str, session_data: dict[str, Any]) -> None:
        conn = self._connections.get(sid)
        if conn:
            conn.session_data = session_data

    def add_room(self, sid: str, room: str) -> None:
        conn = self._connections.get(sid)
        if conn:
            conn.rooms.add(room)

    def remove_room(self, sid: str, room: str) -> None:
        conn = self._connections.get(sid)
        if conn:
            conn.rooms.discard(room)

    def get_all_connections(self) -> list[Connection]:
        return list(self._connections.values())

    def get_connections_data(self) -> list[dict[str, Any]]:
        return [conn.to_dict() for conn in self._connections.values()]

    @property
    def connection_count(self) -> int:
        return len(self._connections)


connection_manager = ConnectionManager()
