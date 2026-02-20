# SocketIO API Reference

## HTTP Endpoints

### `GET /` or `GET /dashboard`
Web dashboard showing active connections.

**Returns:** HTML page with:
- Active connection count
- Table of connections (Session ID, Client IP, Connected At, Rooms)
- Auto-refreshes every 5 seconds

---

### `GET /api/connections`
JSON API for connection data.

**Returns:**
```json
{
  "count": 2,
  "connections": [
    {
      "sid": "abc123",
      "client_ip": "192.168.1.100",
      "connected_at": "2026-02-20T12:00:00+00:00",
      "rooms": ["general", "chat"]
    }
  ]
}
```

---

### `GET /api/logs`
JSON API for message traffic logs.

**Returns:**
```json
{
  "count": 10,
  "logs": [
    {
      "event": "message",
      "from": "abc123",
      "room": null,
      "data": {"text": "hello"},
      "timestamp": "2026-02-20T12:00:00+00:00"
    }
  ]
}
```

---

### `POST /api/logs/clear`
Clear all message logs.

**Returns:**
```json
{"status": "cleared"}
```

---

### `POST /api/disconnect/<sid>`
Disconnect a specific client by session ID.

**Returns:**
```json
{"status": "disconnected", "sid": "abc123"}
```

**Errors:**
- `404` - Client not found
- `500` - Server not initialized

---

## Admin SocketIO Events

## Admin SocketIO Events

Dashboard clients should join `admin_room` to receive real-time updates:

```javascript
socket.emit('join_room', 'admin_room');
```

### `admin:connection`
Emitted when a client connects.

**Data:**
```json
{
  "sid": "abc123",
  "client_ip": "192.168.1.100",
  "connected_at": "2026-02-20T12:00:00+00:00"
}
```

---

### `admin:disconnection`
Emitted when a client disconnects.

**Data:**
```json
{"sid": "abc123"}
```

---

### `admin:message`
Emitted for all message events.

**Data:**
```json
{
  "event": "message",
  "from": "abc123",
  "room": "general",
  "data": {"text": "hello"},
  "timestamp": "2026-02-20T12:00:00+00:00"
}
```

**Events logged:** `message`, `newMessage`, `broadcast`, `join_room`, `leave_room`, `room_message`

---

## SocketIO Connection Events

### `connect`
Fired when client connects.

**Server receives:**
- `sid` - Session ID
- `environ` - ASGI environment dict
- `auth` - Optional auth data from client

**Server returns:** `True` to accept, `False` to reject

---

### `disconnect`
Fired when client disconnects.

**Server receives:**
- `sid` - Session ID

---

## Message Events

### `message`
Send a message to all connected clients.

**Client emits:**
```json
"message", <any data>
```

**Server response:**
```json
{"status": "received", "sid": "<sender_sid>"}
```

**Server broadcasts:**
```json
"message", {"from": "<sid>", "data": <original_data>}
```

---

### `broadcast`
Broadcast message to all clients except sender.

**Client emits:**
```json
"broadcast", <any data>
```

**Server response:**
```json
{"status": "broadcasted"}
```

**Server broadcasts:**
```json
"broadcast", {"from": "<sid>", "data": <original_data>}
```

---

## Room Events

### `join_room`
Join a specific room.

**Client emits:**
```json
"join_room", "<room_name>"
```

**Server response:**
```json
{"status": "joined", "room": "<room_name>"}
```

**Server emits to room:**
```json
"room_joined", {"room": "<room_name>", "sid": "<sid>"}
```

---

### `leave_room`
Leave a specific room.

**Client emits:**
```json
"leave_room", "<room_name>"
```

**Server response:**
```json
{"status": "left", "room": "<room_name>"}
```

**Server emits to room:**
```json
"room_left", {"room": "<room_name>", "sid": "<sid>"}
```

---

### `room_message`
Send message to a specific room.

**Client emits:**
```json
"room_message", {"room": "<room_name>", "message": <any>}
```

**Server response:**
```json
{"status": "sent", "room": "<room_name>"}
```
or on error:
```json
{"status": "error", "message": "Missing room or message"}
```

**Server emits to room (excluding sender):**
```json
"room_message", {"from": "<sid>", "room": "<room_name>", "message": <original>}
```

---

## Utility Events

### `ping`
Health check ping.

**Client emits:**
```json
"ping"
```

**Server response:**
```json
{"status": "pong", "sid": "<sid>"}
```
