# Configuration

## Environment Variables

All configuration is via environment variables prefixed with `SOCKETIO_`.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `SOCKETIO_HOST` | str | `0.0.0.0` | Server bind address |
| `SOCKETIO_PORT` | int | `8000` | Server port |
| `SOCKETIO_CORS_ORIGINS` | str | `*` | Allowed CORS origins (comma-separated or `*`) |
| `SOCKETIO_CORS_METHODS` | str | `GET,POST,PUT,DELETE,OPTIONS` | Allowed HTTP methods |
| `SOCKETIO_CORS_HEADERS` | str | `Content-Type,Authorization` | Allowed headers |
| `SOCKETIO_CORS_CREDENTIALS` | bool | `True` | Allow credentials |
| `SOCKETIO_PING_TIMEOUT` | int | `60` | Ping timeout in seconds |
| `SOCKETIO_PING_INTERVAL` | int | `25` | Ping interval in seconds |
| `SOCKETIO_MAX_HTTP_BUFFER_SIZE` | int | `1000000` | Max HTTP buffer size (1MB) |
| `SOCKETIO_ASYNC_MODE` | str | `asgi` | Async mode (don't change) |
| `SOCKETIO_LOGGER_LEVEL` | str | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR) |
| `SOCKETIO_ALWAYS_CONNECT` | bool | `False` | Connect without waiting for auth |

## Configuration File

Create `.env` file in project root:
```bash
cp .env.example .env
```

Example `.env`:
```env
SOCKETIO_HOST=0.0.0.0
SOCKETIO_PORT=8000
SOCKETIO_CORS_ORIGINS=http://localhost:3000,https://example.com
SOCKETIO_LOGGER_LEVEL=DEBUG
```

## Settings Object

Access in code:
```python
from app.config import settings

print(settings.host)          # "0.0.0.0"
print(settings.port)          # 8000
print(settings.cors_origins_list)  # ["*"] or parsed list
```

## Adding New Settings

1. Add field to `Settings` class in `config.py`:
```python
class Settings(BaseSettings):
    # ... existing fields
    new_option: str = "default_value"
```

2. Use via environment variable:
```bash
export SOCKETIO_NEW_OPTION="custom_value"
```
