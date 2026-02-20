import logging
import sys
from typing import TextIO

from app.config import settings


def setup_logging(stream: TextIO | None = None) -> logging.Logger:
    logger = logging.getLogger("socketio.server")
    logger.setLevel(getattr(logging, settings.logger_level.upper()))

    if not logger.handlers:
        handler = logging.StreamHandler(stream or sys.stdout)
        handler.setLevel(getattr(logging, settings.logger_level.upper()))
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logging()
