# SocketIO API Reference

## Connection Events

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

---

## Admin Events

Admin events are used by the dashboard for monitoring. Admin clients must emit `admin_subscribe` to join the admin room and receive updates.

### `admin_subscribe`
Subscribe to admin events.

**Client emits:**
```json
"admin_subscribe"
```

**Server response:**
```json
{
  "status": "subscribed",
  "connections": [
    {
      "sid": "<sid>",
      "connected_at": "2026-02-20T12:00:00",
      "rooms": ["room1"],
      "client_info": {
        "user_agent": "Mozilla/5.0...",
        "remote_addr": "127.0.0.1",
        "auth": null
      }
    }
  ],
  "total": 5
}
```

---

### `admin_get_connections`
Get all current connections.

**Client emits:**
```json
"admin_get_connections"
```

**Server response:**
```json
{
  "connections": [...],
  "total": 5
}
```

---

### `admin:connection_update` (Server Event)
Broadcast to admin room on connect/disconnect.

**Server emits:**
```json
{
  "type": "connect" | "disconnect",
  "connection": {
    "sid": "<sid>",
    "connected_at": "2026-02-20T12:00:00",
    "rooms": [],
    "client_info": {...}
  },
  "total": 5
}
```

---

### `admin:room_update` (Server Event)
Broadcast to admin room on room join/leave.

**Server emits:**
```json
{
  "type": "join" | "leave",
  "sid": "<sid>",
  "room": "<room_name>",
  "connection": {...}
}
```
