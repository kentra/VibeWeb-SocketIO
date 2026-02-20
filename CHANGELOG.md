# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Web dashboard at `/` to view active SocketIO connections in real-time
- `/api/connections` JSON endpoint for programmatic access to connection data
- Client IP address display in dashboard (supports X-Forwarded-For proxy header)
- `connections.py` - Connection manager to track active sessions and room membership
- `dashboard.py` - HTTP handler for serving the web dashboard
- Dashboard auto-refreshes every 5 seconds
- Comprehensive test suite with 38 tests covering connections, dashboard, and events
- `test_connections.py` - Tests for ConnectionManager and Connection dataclass
- `test_dashboard.py` - Tests for HTML dashboard and JSON API
- `test_events.py` - Tests for event logic and response formats

### Changed
- Updated CONTEXT documentation to reflect current architecture and features
- Default port changed to 5556

### Added (Earlier)
- CHANGELOG.md for tracking project changes
- `.dockerignore` for optimized Docker builds
- Updated CONTEXT documentation with Docker and Kubernetes sections

## [0.1.0] - 2026-02-20

### Added
- Initial release of VibeWeb-SocketIO
- Socket.IO server with real-time bidirectional communication
- Room-based messaging for group communication
- Broadcast messaging to all connected clients
- Configurable CORS support via environment variables
- Graceful shutdown handling (SIGINT, SIGTERM)
- Health check via ping/pong event
- Configuration via pydantic-settings with environment variables
- Docker support with multi-stage build
- Kubernetes deployment manifests (ConfigMap, Deployment, Service, Ingress)
- Project documentation in README.md
