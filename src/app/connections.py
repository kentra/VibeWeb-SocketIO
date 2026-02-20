from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class Connection:
    sid: str
    client_ip: str = ""
    connected_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    rooms: set[str] = field(default_factory=set)


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, Connection] = {}

    def add(self, sid: str, client_ip: str = "") -> Connection:
        conn = Connection(sid=sid, client_ip=client_ip)
        self._connections[sid] = conn
        return conn

    def remove(self, sid: str) -> None:
        self._connections.pop(sid, None)

    def get(self, sid: str) -> Connection | None:
        return self._connections.get(sid)

    def add_room(self, sid: str, room: str) -> None:
        conn = self._connections.get(sid)
        if conn:
            conn.rooms.add(room)

    def remove_room(self, sid: str, room: str) -> None:
        conn = self._connections.get(sid)
        if conn:
            conn.rooms.discard(room)

    def all(self) -> list[Connection]:
        return list(self._connections.values())

    def count(self) -> int:
        return len(self._connections)


manager = ConnectionManager()
