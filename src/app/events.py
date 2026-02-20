from typing import Any

import socketio

from app.connections import manager
from app.logging_config import logger


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
        return True

    @sio.event
    async def disconnect(sid: str) -> None:
        logger.info(f"Client disconnecting: {sid}")
        session = await sio.get_session(sid)
        if session:
            logger.debug(f"Session data for {sid}: {session}")
        manager.remove(sid)
        logger.info(f"Client disconnected: {sid}")

    @sio.event
    async def message(sid: str, data: Any) -> Any:
        logger.info(f"Message from {sid}: {data}")
        await sio.emit("message", {"from": sid, "data": data}, skip_sid=sid)
        return {"status": "received", "sid": sid}

    @sio.event
    async def join_room(sid: str, room: str) -> dict[str, str]:
        logger.info(f"Client {sid} joining room: {room}")
        await sio.enter_room(sid, room)
        manager.add_room(sid, room)
        await sio.emit("room_joined", {"room": room, "sid": sid}, to=room)
        return {"status": "joined", "room": room}

    @sio.event
    async def leave_room(sid: str, room: str) -> dict[str, str]:
        logger.info(f"Client {sid} leaving room: {room}")
        await sio.leave_room(sid, room)
        manager.remove_room(sid, room)
        await sio.emit("room_left", {"room": room, "sid": sid}, to=room)
        return {"status": "left", "room": room}

    @sio.event
    async def room_message(sid: str, data: dict[str, Any]) -> dict[str, str]:
        room = data.get("room")
        message = data.get("message")
        if not room or message is None:
            return {"status": "error", "message": "Missing room or message"}
        logger.info(f"Room message from {sid} to {room}: {message}")
        await sio.emit(
            "room_message", {"from": sid, "room": room, "message": message}, to=room, skip_sid=sid
        )
        return {"status": "sent", "room": room}

    @sio.event
    async def broadcast(sid: str, data: Any) -> dict[str, str]:
        logger.info(f"Broadcast from {sid}: {data}")
        await sio.emit("broadcast", {"from": sid, "data": data}, skip_sid=sid)
        return {"status": "broadcasted"}

    @sio.event
    async def ping(sid: str) -> dict[str, str]:
        return {"status": "pong", "sid": sid}
