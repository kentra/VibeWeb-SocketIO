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
├── __init__.py         # Package init, version
├── config.py           # Settings via pydantic-settings
├── events.py           # SocketIO event handlers
├── logging_config.py   # Logging setup
└── main.py             # Server creation and entry point

tests/
└── test_main.py        # Basic tests

CONTEXT/                 # LLM context documentation
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

## Default Configuration
- Host: `0.0.0.0`
- Port: `8000`
- CORS: All origins (`*`)
- Ping timeout: 60s
- Ping interval: 25s
