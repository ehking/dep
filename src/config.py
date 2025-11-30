"""Application configuration for default settings and constants."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ResolutionSetting:
    label: str
    width: int
    height: int


@dataclass
class DefaultConfig:
    """Container for default UI and rendering settings."""

    fonts: List[str] = field(
        default_factory=lambda: [
            "Vazir",
            "Nazli",
            "Sahel",
            "Shabnam",
        ]
    )
    resolutions: List[ResolutionSetting] = field(
        default_factory=lambda: [
            ResolutionSetting("720p", 1280, 720),
            ResolutionSetting("1080p", 1920, 1080),
            ResolutionSetting("4K", 3840, 2160),
        ]
    )
    fps_options: List[int] = field(default_factory=lambda: [24, 30, 60])
    output_formats: List[str] = field(default_factory=lambda: ["mp4", "gif"])
    transition_styles: List[str] = field(
        default_factory=lambda: [
            "fade",
            "slide",
            "typewriter",
            "scroll",
            "crossfade",
        ]
    )
    animation_styles: Dict[str, str] = field(
        default_factory=lambda: {
            "typewriter": "نوشتار ماشینی",
            "fade": "محو شدنی",
            "scroll": "حرکت عمودی",
            "reveal": "نمایش تدریجی",
        }
    )
    sample_text: str = (
        "سلام! این یک متن آزمایشی برای ساخت موشن گرافیک فارسی است."
    )


def load_default_config() -> DefaultConfig:
    return DefaultConfig()
