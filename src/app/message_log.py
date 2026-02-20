from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class MessageLog:
    event: str
    from_sid: str | None = None
    to_room: str | None = None
    data: Any = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


class MessageLogger:
    def __init__(self, max_size: int = 500) -> None:
        self._logs: deque[MessageLog] = deque(maxlen=max_size)
        self._max_size = max_size

    def log(
        self, event: str, from_sid: str | None = None, to_room: str | None = None, data: Any = None
    ) -> MessageLog:
        entry = MessageLog(event=event, from_sid=from_sid, to_room=to_room, data=data)
        self._logs.append(entry)
        return entry

    def all(self) -> list[MessageLog]:
        return list(self._logs)

    def clear(self) -> None:
        self._logs.clear()

    def count(self) -> int:
        return len(self._logs)


msg_logger = MessageLogger()
