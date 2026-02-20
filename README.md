# VibeWeb-SocketIO

A production-ready Socket.IO server built with Python for real-time bidirectional communication.

## Features

- Real-time bidirectional communication via Socket.IO
- Room-based messaging for group communication
- Broadcast messaging to all connected clients
- Configurable CORS support
- Graceful shutdown handling
- Health check via ping/pong
- Connection tracking with admin events
- Web dashboard for monitoring active connections

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended package manager)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd VibeWeb-SocketIO

# Install dependencies with uv
uv sync --all-extras
```

## Configuration

Create a `.env` file (see `.env.example`):

```env
SOCKETIO_HOST=0.0.0.0
SOCKETIO_PORT=8000
SOCKETIO_CORS_ORIGINS=*
SOCKETIO_LOGGER_LEVEL=INFO
```

### Available Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `SOCKETIO_HOST` | `0.0.0.0` | Server host |
| `SOCKETIO_PORT` | `8000` | Server port |
| `SOCKETIO_CORS_ORIGINS` | `*` | Comma-separated allowed CORS origins |
| `SOCKETIO_CORS_METHODS` | `GET,POST,PUT,DELETE,OPTIONS` | Allowed CORS methods |
| `SOCKETIO_CORS_HEADERS` | `Content-Type,Authorization` | Allowed CORS headers |
| `SOCKETIO_CORS_CREDENTIALS` | `True` | Allow credentials in CORS |
| `SOCKETIO_PING_TIMEOUT` | `60` | Ping timeout in seconds |
| `SOCKETIO_PING_INTERVAL` | `25` | Ping interval in seconds |
| `SOCKETIO_LOGGER_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR) |

## Usage

### Start the Server

```bash
# Using the entry point
uv run server

# Or run directly
uv run python -m app.main
```

The server will start at `http://0.0.0.0:8000` by default.

### Development

```bash
# Run tests
uv run pytest tests/ -v

# Lint code
uv run ruff check src/

# Format code
uv run ruff format src/
```

## API Reference

### Connection Events

#### `connect`
Fired when a client connects. Optionally accepts auth data.

#### `disconnect`
Fired when a client disconnects.

### Message Events

#### `message`
Send a message to all connected clients.

```javascript
// Client emits
socket.emit('message', { text: 'Hello!' });

// Server broadcasts to all other clients
// Event: "message", Data: { from: "<sid>", data: { text: 'Hello!' } }

// Server response
{ status: 'received', sid: '<sender_sid>' }
```

#### `broadcast`
Broadcast a message to all clients except sender.

```javascript
socket.emit('broadcast', { text: 'Hello everyone!' });
// Response: { status: 'broadcasted' }
```

### Room Events

#### `join_room`
Join a specific room.

```javascript
socket.emit('join_room', 'chatroom-1');
// Response: { status: 'joined', room: 'chatroom-1' }
// Other room members receive: { room: 'chatroom-1', sid: '<sid>' }
```

#### `leave_room`
Leave a specific room.

```javascript
socket.emit('leave_room', 'chatroom-1');
// Response: { status: 'left', room: 'chatroom-1' }
```

#### `room_message`
Send a message to a specific room.

```javascript
socket.emit('room_message', { room: 'chatroom-1', message: 'Hi room!' });
// Response: { status: 'sent', room: 'chatroom-1' }
// Room members receive: { from: '<sid>', room: 'chatroom-1', message: 'Hi room!' }
```

### Utility Events

#### `ping`
Health check.

```javascript
socket.emit('ping');
// Response: { status: 'pong', sid: '<sid>' }
```

### Admin Events

#### `admin_subscribe`
Subscribe to admin events for real-time monitoring.

```javascript
socket.emit('admin_subscribe');
// Response: { status: 'subscribed', connections: [...], total: 5 }
```

#### `admin_get_connections`
Get all current connections.

```javascript
socket.emit('admin_get_connections');
// Response: { connections: [...], total: 5 }
```

#### Server Events for Admins

Admins receive these events after subscribing:

- `admin:connection_update` - On client connect/disconnect
- `admin:room_update` - On room join/leave events

## Example Client

```javascript
import { io } from 'socket.io-client';

const socket = io('http://localhost:8000');

socket.on('connect', () => {
  console.log('Connected:', socket.id);
  
  // Join a room
  socket.emit('join_room', 'general');
  
  // Send a room message
  socket.emit('room_message', { room: 'general', message: 'Hello!' });
});

socket.on('message', (data) => {
  console.log('Message:', data);
});

socket.on('room_message', (data) => {
  console.log('Room message:', data);
});
```

## Dashboard

A web GUI dashboard built with [Reflex](https://reflex.dev/) for monitoring active connections.

### Run Dashboard

```bash
# Terminal 1: Start the SocketIO server
uv run server

# Terminal 2: Start the dashboard
cd dashboard && reflex run
```

The dashboard will be available at `http://localhost:3001`.

### Features

- Real-time connection count
- View all active connections
- See client information (user agent, IP address)
- Track room membership per connection
- Connection/disconnection event notifications

## Kubernetes Deployment

### Build and Push Image

```bash
docker build -t vibeweb-socketio:latest .
docker tag vibeweb-socketio:latest your-registry/vibeweb-socketio:latest
docker push your-registry/vibeweb-socketio:latest
```

### Deploy to Kubernetes

```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

### Verify Deployment

```bash
kubectl get pods -l app=vibeweb-socketio
kubectl get services
kubectl logs -l app=vibeweb-socketio
```

### Configuration

Edit `k8s/configmap.yaml` to customize environment variables. The ingress assumes an nginx ingress controller with WebSocket support.

## Project Structure

```
src/app/
├── __init__.py              # Package init
├── config.py                # Settings via pydantic-settings
├── connection_manager.py    # Connection tracking
├── events.py                # SocketIO event handlers
├── logging_config.py        # Logging setup
└── main.py                  # Server entry point

dashboard/
├── dashboard/
│   ├── __init__.py          # Package init
│   └── dashboard.py         # Reflex web dashboard
├── rxconfig.py              # Reflex configuration
└── requirements.txt         # Dashboard dependencies

k8s/
├── configmap.yaml           # Kubernetes ConfigMap
├── deployment.yaml          # Kubernetes Deployment
├── service.yaml             # Kubernetes Service
└── ingress.yaml             # Kubernetes Ingress

tests/
└── test_main.py             # Tests
```

## License

MIT
