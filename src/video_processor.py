"""Video handling utilities for previews and trimming."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class VideoSelection:
    path: Optional[Path]
    start_time: float
    end_time: float
    volume: float


class VideoProcessor:
    """Stores and validates video configuration for Manim scenes."""

    def __init__(self) -> None:
        self.selection = VideoSelection(path=None, start_time=0.0, end_time=0.0, volume=1.0)
        logger.info("Initialized VideoProcessor with empty selection")

    def select_file(self, file_path: str) -> None:
        path = Path(file_path)
        if not path.exists():
            logger.error("Video file not found: %s", file_path)
            raise FileNotFoundError(f"Video file not found: {file_path}")
        self.selection.path = path
        logger.info("Selected video file: %s", file_path)

    def update_trim(self, start: float, end: float) -> None:
        if start < 0 or end < 0:
            raise ValueError("Start and end times must be non-negative")
        if end and start > end:
            raise ValueError("Start time cannot exceed end time")
        self.selection.start_time = start
        self.selection.end_time = end
        logger.debug("Updated trim to start=%s end=%s", start, end)

    def set_volume(self, volume: float) -> None:
        if not 0.0 <= volume <= 1.0:
            raise ValueError("Volume must be between 0 and 1")
        self.selection.volume = volume
        logger.debug("Volume set to %.2f", volume)

    def describe(self) -> str:
        return (
            f"File: {self.selection.path}, "
            f"Start: {self.selection.start_time}s, End: {self.selection.end_time}s, "
            f"Volume: {self.selection.volume}"
        )
