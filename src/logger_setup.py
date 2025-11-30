"""Logging utilities for the Persian Motion Graphics Creator."""

import logging
from pathlib import Path

LOG_PATH = Path("logs")
LOG_FILE = LOG_PATH / "application.log"


def configure_logging() -> None:
    LOG_PATH.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logging.getLogger(__name__).info("Logging initialized. Log file at %s", LOG_FILE)
