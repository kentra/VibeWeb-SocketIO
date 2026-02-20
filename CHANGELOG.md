# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- **Real-time WebSocket updates for dashboard** - Dashboard now uses WebSocket connection to receive instant updates instead of polling every 5 seconds
- **Disconnect clients from dashboard** - Added ability to disconnect specific clients directly from the admin dashboard via `/api/disconnect/<sid>` endpoint
- **Message traffic logging** - New message log feature shows all events (messages, broadcasts, room joins/leaves) in real-time
- **Message log API** - Added `/api/logs` endpoint to retrieve logged messages and `/api/logs/clear` to clear the log
- **Admin room for real-time events** - Dashboard clients join `admin_room` to receive `admin:connection`, `admin:disconnection`, and `admin:message` events
- `message_log.py` - New module with `MessageLogger` class for tracking message traffic (configurable max size, default 500 entries)
- `ADMIN_ROOM` constant in `connections.py` for the admin broadcast room
- `set_socketio_server()` function in dashboard to enable disconnect functionality
- Tabbed interface in dashboard with "Connections" and "Message Log" tabs
- Clear logs button in the message log tab
- Visual connection status indicator showing WebSocket connection state
- Toast notifications for connection/disconnection events
- 18 new tests for message logging and dashboard enhancements (56 total tests)
- `test_message_log.py` - New test file for MessageLogger functionality

### Changed
- Dashboard now establishes a SocketIO connection for real-time updates instead of HTTP polling
- Event handlers now emit admin events to the admin room for dashboard updates
- All message events are now logged to the message logger for traffic monitoring
- Project structure updated with new `message_log.py` module

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
