# Project Overview

## Summary
Production-ready SocketIO server built with Python, python-socketio, and uvicorn. Designed for real-time bidirectional communication between clients and server.

## Tech Stack
- **Python 3.12+**
- **python-socketio** - Socket.IO server implementation
- **uvicorn** - ASGI server with uvloop for performance
- **pydantic / pydantic-settings** - Configuration management
- **aiohttp** - Async HTTP client (available for extensions)

## Project Structure
```
src/app/
├── __init__.py              # Package init, version
├── config.py                # Settings via pydantic-settings
├── connection_manager.py    # Connection tracking
├── events.py                # SocketIO event handlers
├── logging_config.py        # Logging setup
└── main.py                  # Server creation and entry point

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
└── test_main.py             # Basic tests

CONTEXT/                      # LLM context documentation
```

## Quick Start
```bash
# Install dependencies
uv sync --all-extras

# Run server
uv run python -m app.main

# Or use the entry point
uv run server

# Run tests
uv run pytest tests/ -v

# Lint
uv run ruff check src/
```

## Dashboard

```bash
# Install dashboard dependencies
uv sync --all-extras

# Run the server (in one terminal)
uv run server

# Run the dashboard (in another terminal)
cd dashboard && reflex run
```

The dashboard provides real-time monitoring of:
- Active connections
- Room membership per connection
- Client information (user agent, IP)
- Connection/disconnection events

## Docker

```bash
# Build image
docker build -t vibeweb-socketio:latest .

# Run container
docker run -p 8000:8000 vibeweb-socketio:latest
```

## Kubernetes

```bash
# Deploy to cluster
kubectl apply -f k8s/

# Check status
kubectl get pods -l app=vibeweb-socketio
```

## Default Configuration
- Host: `0.0.0.0`
- Port: `8000`
- CORS: All origins (`*`)
- Ping timeout: 60s
- Ping interval: 25s
