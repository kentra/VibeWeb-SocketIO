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
    └─→ socketio.ASGIApp(sio, other_asgi_app=dashboard_app) → app
```

The ASGI app routes requests:
- SocketIO connections go to the SocketIO server
- HTTP requests go to `dashboard_app` for the web dashboard

## Key Components

### 1. Configuration (config.py)
- Uses `pydantic-settings` for type-safe configuration
- Environment variables prefixed with `SOCKETIO_`
- Single `settings` instance exported

### 2. Connection Manager (connections.py)
- `Connection` dataclass: stores sid, client_ip, connected_at, rooms
- `ConnectionManager` class: tracks all active connections
- `ADMIN_ROOM` constant: "admin_room" - special room for dashboard clients
- Global `manager` instance used by event handlers
- Methods: `add()`, `remove()`, `get()`, `add_room()`, `remove_room()`, `all()`, `count()`

### 3. Event Handlers (events.py)
- All event handlers registered via `register_events(sio)`
- Handlers are defined as nested functions with `@sio.event` decorator
- Session management via `sio.save_session()` / `sio.get_session()`
- Connection tracking via `manager.add()` / `manager.remove()`
- Client IP extracted from `X-Forwarded-For` or `REMOTE_ADDR`

### 4. Dashboard (dashboard.py)
- `get_dashboard_html()` - Returns HTML dashboard with real-time WebSocket updates
- `get_connections_json()` - Returns JSON with active connections
- `get_logs_json()` - Returns JSON with message traffic logs
- `set_socketio_server(sio)` - Stores sio reference for disconnect functionality
- `dashboard_app()` - ASGI handler for HTTP routes:
  - `/` or `/dashboard` - Web dashboard HTML
  - `/api/connections` - JSON API for connection data
  - `/api/logs` - JSON API for message logs
  - `/api/logs/clear` (POST) - Clear message logs
  - `/api/disconnect/<sid>` (POST) - Disconnect a client
  - All other paths return 404

### 5. Message Logger (message_log.py)
- `MessageLog` dataclass: stores event, from_sid, to_room, data, timestamp
- `MessageLogger` class: circular buffer for message traffic (default max 500 entries)
- Global `msg_logger` instance for tracking all events
- Methods: `log()`, `all()`, `clear()`, `count()`

### 6. Logging (logging_config.py)
- Structured logging with timestamps
- Configurable log level via `SOCKETIO_LOGGER_LEVEL`
- Single logger instance for consistent formatting

### 7. Server (main.py)
- `create_socketio_server()` - Creates configured AsyncServer
- `create_app()` - Creates ASGI app with SocketIO + dashboard
- `run_server()` - Entry point with signal handling

## ASGI Application

The server runs as an ASGI application using:
- `socketio.ASGIApp` wraps the AsyncServer
- `other_asgi_app=dashboard_app` handles HTTP requests
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

Room membership is also tracked in `ConnectionManager` for dashboard display.

## Connection Tracking

When a client connects:
1. `connect` handler extracts client IP from environ
2. `manager.add(sid, client_ip)` creates a `Connection` record
3. Connection stored in `manager._connections` dict
4. `admin:connection` event emitted to `admin_room`

When a client disconnects:
1. `disconnect` handler calls `manager.remove(sid)`
2. Connection record removed from manager
3. `admin:disconnection` event emitted to `admin_room`

## Admin Room System

Dashboard clients join the special `admin_room` to receive real-time updates:

- `admin:connection` - Emitted when a client connects
  ```json
  {"sid": "abc123", "client_ip": "192.168.1.1", "connected_at": "2026-02-20T12:00:00+00:00"}
  ```

- `admin:disconnection` - Emitted when a client disconnects
  ```json
  {"sid": "abc123"}
  ```

- `admin:message` - Emitted for all message events (message, broadcast, join_room, leave_room, room_message)
  ```json
  {"event": "message", "from": "abc123", "data": {...}, "timestamp": "2026-02-20T12:00:00+00:00"}
  ```

All events are also logged to the `MessageLogger` for the `/api/logs` endpoint.
