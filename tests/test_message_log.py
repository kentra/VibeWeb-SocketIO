import json

import pytest

from app.message_log import MessageLog, MessageLogger, msg_logger


class TestMessageLog:
    def test_message_log_defaults(self):
        log = MessageLog(event="test")
        assert log.event == "test"
        assert log.from_sid is None
        assert log.to_room is None
        assert log.data is None
        assert log.timestamp is not None

    def test_message_log_with_all_fields(self):
        log = MessageLog(
            event="message", from_sid="sid-1", to_room="room-1", data={"text": "hello"}
        )
        assert log.event == "message"
        assert log.from_sid == "sid-1"
        assert log.to_room == "room-1"
        assert log.data == {"text": "hello"}


class TestMessageLogger:
    def test_log_creates_entry(self):
        logger = MessageLogger()
        entry = logger.log(event="test", from_sid="sid-1", data="hello")
        assert entry.event == "test"
        assert entry.from_sid == "sid-1"
        assert entry.data == "hello"

    def test_all_returns_entries(self):
        logger = MessageLogger()
        logger.log(event="msg1")
        logger.log(event="msg2")
        entries = logger.all()
        assert len(entries) == 2
        events = {e.event for e in entries}
        assert events == {"msg1", "msg2"}

    def test_clear_removes_all_entries(self):
        logger = MessageLogger()
        logger.log(event="msg1")
        logger.log(event="msg2")
        assert logger.count() == 2
        logger.clear()
        assert logger.count() == 0

    def test_count(self):
        logger = MessageLogger()
        assert logger.count() == 0
        logger.log(event="msg1")
        assert logger.count() == 1
        logger.log(event="msg2")
        assert logger.count() == 2

    def test_max_size_limit(self):
        logger = MessageLogger(max_size=3)
        logger.log(event="msg1")
        logger.log(event="msg2")
        logger.log(event="msg3")
        logger.log(event="msg4")
        assert logger.count() == 3
        events = {e.event for e in logger.all()}
        assert "msg1" not in events
        assert "msg4" in events

    def test_global_msg_logger(self):
        original_count = msg_logger.count()
        msg_logger.log(event="test_global")
        assert msg_logger.count() == original_count + 1
        msg_logger.clear()
