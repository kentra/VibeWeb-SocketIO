# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
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
