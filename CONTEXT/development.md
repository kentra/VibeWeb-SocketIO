# Development Guide

## Prerequisites
- Python 3.12+
- uv package manager

## Setup

```bash
# Install all dependencies (including dev)
uv sync --all-extras

# Create .env from example
cp .env.example .env
```

## Running the Server

```bash
# Development
uv run python -m app.main

# Or via entry point
uv run server
```

Server runs at `http://0.0.0.0:8000`

## Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test
uv run pytest tests/test_main.py -v

# Run with coverage (if needed)
uv run pytest tests/ --cov=app
```

## Linting

```bash
# Check for issues
uv run ruff check src/

# Auto-fix issues
uv run ruff check src/ --fix

# Format code
uv run ruff format src/
```

## Adding New Event Handlers

1. Open `src/app/events.py`
2. Add new handler inside `register_events()`:
```python
@sio.event
async def my_event(sid: str, data: Any) -> dict[str, Any]:
    logger.info(f"my_event from {sid}: {data}")
    # Process data
    await sio.emit("my_response", {"result": "ok"})
    return {"status": "success"}
```

## Adding New Configuration

1. Add field to `Settings` in `config.py`
2. Add to `.env.example`
3. Document in `configuration.md`

## Debugging

Set log level to debug:
```bash
export SOCKETIO_LOGGER_LEVEL=DEBUG
uv run python -m app.main
```

## Testing SocketIO Connections

Use the SocketIO client library:
```python
import socketio

sio = socketio.Client()
sio.connect("http://localhost:8000")

@sio.on("message")
def on_message(data):
    print(f"Received: {data}")

sio.emit("message", {"text": "hello"})
```

## Docker

```bash
# Build image
docker build -t vibeweb-socketio:latest .

# Run container locally
docker run -p 8000:8000 vibeweb-socketio:latest

# Run with custom config
docker run -p 8000:8000 -e SOCKETIO_LOGGER_LEVEL=DEBUG vibeweb-socketio:latest
```

## Kubernetes Deployment

```bash
# Apply all manifests
kubectl apply -f k8s/

# Or apply individually
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# View deployment status
kubectl get pods -l app=vibeweb-socketio
kubectl logs -l app=vibeweb-socketio -f

# Scale deployment
kubectl scale deployment vibeweb-socketio --replicas=3
```

### Kubernetes Configuration

Edit `k8s/configmap.yaml` to change environment variables:
```yaml
data:
  SOCKETIO_HOST: "0.0.0.0"
  SOCKETIO_PORT: "8000"
  SOCKETIO_CORS_ORIGINS: "*"
```

Update the deployment image in `k8s/deployment.yaml`:
```yaml
image: your-registry/vibeweb-socketio:latest
```
