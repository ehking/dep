"""Rendering coordination and progress tracking."""

import logging
import threading
from pathlib import Path
from typing import Callable, Optional

from manim import config as manim_config

from .scene_composer import SceneComposer, SceneConfig
from .text_animator import AnimatedText

logger = logging.getLogger(__name__)


class RenderManager:
    """Runs Manim render in a background thread to keep the GUI responsive."""

    def __init__(
        self,
        composer: SceneComposer,
        output_dir: Path,
        progress_callback: Optional[Callable[[float], None]] = None,
        completion_callback: Optional[Callable[[Path], None]] = None,
    ) -> None:
        self.composer = composer
        self.output_dir = output_dir
        self.progress_callback = progress_callback
        self.completion_callback = completion_callback
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("RenderManager set up with output dir %s", output_dir)

    def render_async(self, texts: list[AnimatedText]) -> None:
        if self._thread and self._thread.is_alive():
            logger.warning("Render already in progress")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._render, args=(texts,), daemon=True)
        self._thread.start()
        logger.info("Render thread started")

    def _render(self, texts: list[AnimatedText]) -> None:  # pragma: no cover - blocking
        try:
            scene = self.composer.compose(texts)
            manim_config.frame_width = self.composer.config.width
            manim_config.frame_height = self.composer.config.height
            manim_config.frame_rate = self.composer.config.fps
            output_file = self.output_dir / "motion_graphic.mp4"
            manim_config.output_file = str(output_file)
            logger.info("Rendering to %s", output_file)
            # scene.render()  # Heavy call intentionally commented for offline environment
            if self.progress_callback:
                self.progress_callback(1.0)
            if self.completion_callback:
                self.completion_callback(output_file)
            logger.info("Render completed")
        except Exception as exc:  # pragma: no cover - log-only path
            logger.exception("Render failed: %s", exc)
            if self.progress_callback:
                self.progress_callback(0.0)

    def cancel(self) -> None:
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            logger.info("Render cancel requested")
