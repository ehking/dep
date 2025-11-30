"""Persian text processing and animation helpers."""

import logging
from dataclasses import dataclass
from typing import List

import arabic_reshaper
from bidi.algorithm import get_display

logger = logging.getLogger(__name__)


@dataclass
class AnimatedText:
    content: str
    font: str
    color: str
    size: int
    animation: str
    duration: float


class PersianTextAnimator:
    """Handles RTL reshaping and prepares Manim-ready text objects."""

    def __init__(self, default_font: str) -> None:
        self.default_font = default_font
        logger.info("Initialized PersianTextAnimator with default font %s", default_font)

    def reshape_text(self, text: str) -> str:
        logger.debug("Reshaping text: %s", text)
        reshaped = arabic_reshaper.reshape(text)
        display = get_display(reshaped)
        logger.debug("Reshaped text result: %s", display)
        return display

    def build_animated_sequence(self, entries: List[AnimatedText]) -> List[AnimatedText]:
        processed: List[AnimatedText] = []
        for entry in entries:
            reshaped = self.reshape_text(entry.content)
            processed_entry = AnimatedText(
                content=reshaped,
                font=entry.font or self.default_font,
                color=entry.color,
                size=entry.size,
                animation=entry.animation,
                duration=entry.duration,
            )
            processed.append(processed_entry)
            logger.info(
                "Prepared animated text '%s' with animation %s for duration %.2f",
                entry.content,
                entry.animation,
                entry.duration,
            )
        return processed

    def typewriter_effect_frames(self, text: str) -> List[str]:
        display_text = self.reshape_text(text)
        frames = [display_text[:i] for i in range(1, len(display_text) + 1)]
        logger.debug("Generated %d typewriter frames for text", len(frames))
        return frames
