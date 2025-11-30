"""Manim scene generation based on UI inputs."""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from manim import BLUE, Scene, Text, VideoFileClip, VGroup

from .text_animator import AnimatedText

logger = logging.getLogger(__name__)


@dataclass
class SceneConfig:
    width: int
    height: int
    fps: int
    background_videos: List[Path] = field(default_factory=list)


class PersianScene(Scene):
    """Custom scene that supports layering Persian text and background video."""

    def __init__(self, scene_config: SceneConfig, animated_texts: List[AnimatedText]):
        self.scene_config = scene_config
        self.animated_texts = animated_texts
        super().__init__()

    def construct(self) -> None:  # pragma: no cover - Manim render path
        logger.info("Starting Manim construct with %d text items", len(self.animated_texts))
        text_group = VGroup()
        y_position = 3
        for animated in self.animated_texts:
            manim_text = Text(
                animated.content,
                font=animated.font,
                color=animated.color,
                font_size=animated.size,
            )
            manim_text.to_edge("left")
            manim_text.shift(y_position * manim_text.get_y() * 0 + y_position)
            text_group.add(manim_text)
            self.play(manim_text.animate.set_opacity(0))
            self.play(manim_text.animate.set_opacity(1), run_time=animated.duration)
            y_position -= 1
        self.play(text_group.animate.set_color(BLUE))

        for video_path in self.scene_config.background_videos:
            clip = VideoFileClip(str(video_path))
            logger.info("Adding background video: %s", video_path)
            self.add(clip)


class SceneComposer:
    """Builds Manim scenes and holds configuration for rendering."""

    def __init__(self, config: SceneConfig):
        self.config = config
        logger.info(
            "SceneComposer initialized with resolution %sx%s at %sfps",
            config.width,
            config.height,
            config.fps,
        )

    def compose(self, texts: List[AnimatedText]) -> PersianScene:
        logger.info("Composing scene with %d text elements", len(texts))
        return PersianScene(scene_config=self.config, animated_texts=texts)
