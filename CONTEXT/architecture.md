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

### 2. Event Handlers (events.py)
- All event handlers registered via `register_events(sio)`
- Handlers are defined as nested functions with `@sio.event` decorator
- Session management via `sio.save_session()` / `sio.get_session()`

### 3. Logging (logging_config.py)
- Structured logging with timestamps
- Configurable log level via `SOCKETIO_LOGGER_LEVEL`
- Single logger instance for consistent formatting

### 4. Server (main.py)
- `create_socketio_server()` - Creates configured AsyncServer
- `create_app()` - Creates ASGI app for uvicorn
- `run_server()` - Entry point with signal handling

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
