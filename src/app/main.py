import signal
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import socketio
import uvicorn
from uvicorn.config import Config
from uvicorn.server import Server

from app.config import settings
from app.dashboard import dashboard_app
from app.events import register_events
from app.logging_config import logger


def create_socketio_server() -> socketio.AsyncServer:
    sio = socketio.AsyncServer(
        async_mode=settings.async_mode,
        cors_allowed_origins=settings.cors_origins_list,
        cors_credentials=settings.cors_credentials,
        ping_timeout=settings.ping_timeout,
        ping_interval=settings.ping_interval,
        max_http_buffer_size=settings.max_http_buffer_size,
        always_connect=settings.always_connect,
        logger=False,
        engineio_logger=False,
    )
    register_events(sio)
    return sio


@asynccontextmanager
async def lifespan(sio: socketio.AsyncServer) -> AsyncIterator[None]:
    logger.info("Starting SocketIO server...")
    yield
    logger.info("Shutting down SocketIO server...")


def create_app() -> socketio.ASGIApp:
    sio = create_socketio_server()
    app = socketio.ASGIApp(sio, other_asgi_app=dashboard_app)
    return app


app = create_app()


async def shutdown_signal_handler(server: Server) -> None:
    logger.info("Shutdown signal received, stopping server...")
    server.should_exit = True


def run_server() -> None:
    config = Config(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.logger_level.lower(),
        reload=False,
    )
    server = Server(config)

    def handle_signal(signum: int, frame: object) -> None:
        logger.info(f"Received signal {signum}")
        import asyncio

        asyncio.create_task(shutdown_signal_handler(server))

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    logger.info(f"Server running at http://{settings.host}:{settings.port}")
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.logger_level.lower(),
    )


if __name__ == "__main__":
    run_server()
