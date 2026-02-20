# Architecture

## Server Initialization Flow

```
main.py:create_app()
    │
    ├─→ create_socketio_server()
    │       │
    │       ├─→ socketio.AsyncServer(config from settings)
    │       └─→ register_events(sio)
    │
    └─→ socketio.ASGIApp(sio) → app
```

## Key Components

### 1. Configuration (config.py)
- Uses `pydantic-settings` for type-safe configuration
- Environment variables prefixed with `SOCKETIO_`
- Single `settings` instance exported

### 2. Connection Manager (connection_manager.py)
- Tracks all active connections in memory
- Stores connection metadata (connect time, rooms, client info)
- Provides connection data for admin dashboard
- Singleton `connection_manager` instance

### 3. Event Handlers (events.py)
- All event handlers registered via `register_events(sio)`
- Handlers are defined as nested functions with `@sio.event` decorator
- Session management via `sio.save_session()` / `sio.get_session()`
- Updates `ConnectionManager` on connect/disconnect/room events
- Emits admin events for dashboard updates

### 4. Logging (logging_config.py)
- Structured logging with timestamps
- Configurable log level via `SOCKETIO_LOGGER_LEVEL`
- Single logger instance for consistent formatting

### 5. Server (main.py)
- `create_socketio_server()` - Creates configured AsyncServer
- `create_app()` - Creates ASGI app for uvicorn
- `run_server()` - Entry point with signal handling

### 6. Dashboard (dashboard/)
- Reflex-based web GUI for monitoring
- Connects to SocketIO server as admin client
- Real-time connection updates

## ASGI Application
The server runs as an ASGI application using:
- `socketio.ASGIApp` wraps the AsyncServer
- `uvicorn` serves the ASGI app
- Supports WebSocket and HTTP long-polling transports

## Session Management
SocketIO sessions store client state:
```python
await sio.save_session(sid, {"connected": True})
session = await sio.get_session(sid)
```

## Room System
Built-in room support:
- `sio.enter_room(sid, room)` - Join room
- `sio.leave_room(sid, room)` - Leave room
- `emit(..., to=room)` - Send to room
- `emit(..., skip_sid=sid)` - Broadcast to others
