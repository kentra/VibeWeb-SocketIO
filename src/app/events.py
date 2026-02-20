from typing import Any

import socketio

from app.connections import ADMIN_ROOM, manager
from app.logging_config import logger
from app.message_log import msg_logger


def _emit_to_admin(sio: socketio.AsyncServer, event: str, data: dict[str, Any]) -> None:
    import asyncio

    asyncio.create_task(sio.emit(event, data, to=ADMIN_ROOM))


def register_events(sio: socketio.AsyncServer) -> None:
    @sio.event
    async def connect(sid: str, environ: dict[str, Any], auth: dict[str, Any] | None) -> bool:
        logger.info(f"Client connecting: {sid}")
        if auth:
            logger.debug(f"Auth data for {sid}: {auth}")
        client_ip = environ.get("HTTP_X_FORWARDED_FOR", environ.get("REMOTE_ADDR", ""))
        if "," in client_ip:
            client_ip = client_ip.split(",")[0].strip()
        manager.add(sid, client_ip)
        await sio.save_session(sid, {"connected": True})
        logger.info(f"Client connected: {sid} from {client_ip}")
        await sio.emit(
            "admin:connection",
            {
                "sid": sid,
                "client_ip": client_ip,
                "connected_at": manager.get(sid).connected_at.isoformat()
                if manager.get(sid)
                else None,
            },
            to=ADMIN_ROOM,
        )
        return True

    @sio.event
    async def disconnect(sid: str) -> None:
        logger.info(f"Client disconnecting: {sid}")
        session = await sio.get_session(sid)
        if session:
            logger.debug(f"Session data for {sid}: {session}")
        await sio.emit("admin:disconnection", {"sid": sid}, to=ADMIN_ROOM)
        manager.remove(sid)
        logger.info(f"Client disconnected: {sid}")

    @sio.event
    async def message(sid: str, data: Any) -> Any:
        logger.info(f"Message from {sid}: {data}")
        entry = msg_logger.log(event="message", from_sid=sid, data=data)
        await sio.emit(
            "admin:message",
            {
                "event": "message",
                "from": sid,
                "data": data,
                "timestamp": entry.timestamp.isoformat(),
            },
            to=ADMIN_ROOM,
        )
        await sio.emit("message", data, skip_sid=sid)
        return {"status": "received", "sid": sid}

    @sio.event
    async def newMessage(sid: str, data: Any) -> Any:
        logger.info(f"Message from {sid}: {data}")
        entry = msg_logger.log(event="newMessage", from_sid=sid, data=data)
        await sio.emit(
            "admin:message",
            {
                "event": "newMessage",
                "from": sid,
                "data": data,
                "timestamp": entry.timestamp.isoformat(),
            },
            to=ADMIN_ROOM,
        )
        await sio.emit("newMessage", data, skip_sid=sid)
        return {"status": "received", "sid": sid}

    @sio.event
    async def join_room(sid: str, room: str) -> dict[str, str]:
        logger.info(f"Client {sid} joining room: {room}")
        await sio.enter_room(sid, room)
        manager.add_room(sid, room)
        entry = msg_logger.log(event="join_room", from_sid=sid, to_room=room, data=None)
        await sio.emit(
            "admin:message",
            {
                "event": "join_room",
                "from": sid,
                "room": room,
                "timestamp": entry.timestamp.isoformat(),
            },
            to=ADMIN_ROOM,
        )
        await sio.emit("room_joined", {"room": room, "sid": sid}, to=room)
        return {"status": "joined", "room": room}

    @sio.event
    async def leave_room(sid: str, room: str) -> dict[str, str]:
        logger.info(f"Client {sid} leaving room: {room}")
        await sio.leave_room(sid, room)
        manager.remove_room(sid, room)
        entry = msg_logger.log(event="leave_room", from_sid=sid, to_room=room, data=None)
        await sio.emit(
            "admin:message",
            {
                "event": "leave_room",
                "from": sid,
                "room": room,
                "timestamp": entry.timestamp.isoformat(),
            },
            to=ADMIN_ROOM,
        )
        await sio.emit("room_left", {"room": room, "sid": sid}, to=room)
        return {"status": "left", "room": room}

    @sio.event
    async def room_message(sid: str, data: dict[str, Any]) -> dict[str, str]:
        room = data.get("room")
        message = data.get("message")
        if not room or message is None:
            return {"status": "error", "message": "Missing room or message"}
        logger.info(f"Room message from {sid} to {room}: {message}")
        entry = msg_logger.log(event="room_message", from_sid=sid, to_room=room, data=message)
        await sio.emit(
            "admin:message",
            {
                "event": "room_message",
                "from": sid,
                "room": room,
                "data": message,
                "timestamp": entry.timestamp.isoformat(),
            },
            to=ADMIN_ROOM,
        )
        await sio.emit(
            "room_message", {"from": sid, "room": room, "message": message}, to=room, skip_sid=sid
        )
        return {"status": "sent", "room": room}

    @sio.event
    async def broadcast(sid: str, data: Any) -> dict[str, str]:
        logger.info(f"Broadcast from {sid}: {data}")
        entry = msg_logger.log(event="broadcast", from_sid=sid, data=data)
        await sio.emit(
            "admin:message",
            {
                "event": "broadcast",
                "from": sid,
                "data": data,
                "timestamp": entry.timestamp.isoformat(),
            },
            to=ADMIN_ROOM,
        )
        await sio.emit("broadcast", {"from": sid, "data": data}, skip_sid=sid)
        return {"status": "broadcasted"}

    @sio.event
    async def ping(sid: str) -> dict[str, str]:
        return {"status": "pong", "sid": sid}
