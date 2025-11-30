"""Automated Persian lyric video generator using Manim.

This module provides the :class:`AutoMusicVideoGenerator` class, which turns a set of
inputs (lyrics, music, background video) into a synchronized lyric video with minimal
configuration. The implementation is intentionally self contained and relies on
best-effort heuristics so that it can operate even when optional dependencies such as
``librosa``, ``pydub``, or ``manim`` are not installed. When Manim is unavailable the
pipeline writes out a storyboard JSON file instead of rendering a video.
"""

from __future__ import annotations

import argparse
import dataclasses
import importlib.util
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

# Optional dependencies
LIBROSA_AVAILABLE = importlib.util.find_spec("librosa") is not None
PYDUB_AVAILABLE = importlib.util.find_spec("pydub") is not None
MANIM_AVAILABLE = importlib.util.find_spec("manim") is not None
PIL_AVAILABLE = importlib.util.find_spec("PIL") is not None

if LIBROSA_AVAILABLE:
    import librosa

if PYDUB_AVAILABLE:
    from pydub import AudioSegment

if MANIM_AVAILABLE:
    from manim import (
        BLUE,
        GREEN,
        ORIGIN,
        PURPLE,
        RED,
        RIGHT,
        DOWN,
        Scene,
        Text,
        FadeIn,
        FadeOut,
        VGroup,
    )
    from manim.utils.color import rgb_to_color

if PIL_AVAILABLE:
    from PIL import Image


@dataclass
class MusicAnalysis:
    tempo: float
    beats: List[float]
    vocals: List[float]
    energy: List[float]
    duration: float
    genre_hint: str


@dataclass
class LyricLine:
    raw_text: str
    processed_text: str
    words: List[str]
    start: float
    end: float
    emphasis: bool
    anchor: str
    color: str


@dataclass
class AnimationDirective:
    line: LyricLine
    animation_style: str
    intensity: float


@dataclass
class ColorPalette:
    primary: str
    secondary: str
    accent: str


class AutoMusicVideoGenerator:
    """Generate a Persian lyric video automatically.

    The generator prioritizes full automation. It makes best-effort use of available
    libraries for music analysis and video rendering while maintaining sensible
    fallbacks.
    """

    def __init__(self) -> None:
        self.palette_cache: dict[Path, ColorPalette] = {}

    # -------------------------- Public API ---------------------------------
    def process_all_inputs(self, lyrics_path: str, music_path: str, video_path: str) -> Path:
        music_file = Path(music_path)
        video_file = Path(video_path)
        lyrics_file = Path(lyrics_path)

        analysis = self.analyze_music(music_file)
        formatted_lyrics = self.auto_format_persian_lyrics(lyrics_file)
        directives = self.auto_generate_animations(formatted_lyrics, analysis, video_file)
        return self.render_auto_video(directives, video_file, music_file, analysis)

    # -------------------------- Music analysis ------------------------------
    def analyze_music(self, music_path: Path) -> MusicAnalysis:
        if LIBROSA_AVAILABLE:
            y, sr = librosa.load(music_path, sr=None, mono=True)
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
            beats = librosa.frames_to_time(beat_frames, sr=sr).tolist()
            onset_env = librosa.onset.onset_strength(y=y, sr=sr).tolist()
            energy = self._normalize_curve(onset_env, target_points=200)
            harmonic, percussive = librosa.effects.hpss(y)
            vocal_energy = self._normalize_curve(harmonic.tolist(), target_points=200)
            duration = librosa.get_duration(y=y, sr=sr)
        elif PYDUB_AVAILABLE:
            audio = AudioSegment.from_file(music_path)
            duration = len(audio) / 1000.0
            tempo = self._estimate_tempo_from_envelope(audio)
            beats = self._distribute_beats(duration, tempo)
            envelope = [segment.dBFS for segment in audio[::200]] or [audio.dBFS]
            energy = self._normalize_curve(envelope, target_points=200)
            vocal_energy = energy
        else:
            duration = self._probe_duration_fallback(music_path)
            tempo = 96.0 if duration == 0 else max(72.0, min(140.0, 240.0 / duration))
            beats = self._distribute_beats(duration, tempo)
            energy = [0.5 for _ in range(200)]
            vocal_energy = energy

        genre_hint = self._genre_from_tempo(tempo)
        return MusicAnalysis(
            tempo=tempo,
            beats=beats,
            vocals=vocal_energy,
            energy=energy,
            duration=duration,
            genre_hint=genre_hint,
        )

    def _probe_duration_fallback(self, music_path: Path) -> float:
        try:
            size_seconds = music_path.stat().st_size / 100000.0
            return size_seconds
        except OSError:
            return 0.0

    def _estimate_tempo_from_envelope(self, audio: "AudioSegment") -> float:
        samples = [segment.dBFS for segment in audio[::500]] or [audio.dBFS]
        peaks = [value for value in samples if value > (sum(samples) / len(samples))]
        if not peaks:
            return 100.0
        peak_distance = max(1, len(samples) / max(len(peaks), 1))
        return max(80.0, min(140.0, 60.0 / peak_distance * 4))

    def _distribute_beats(self, duration: float, tempo: float) -> List[float]:
        if duration <= 0:
            return []
        interval = 60.0 / tempo
        count = max(1, int(duration / interval))
        return [round(i * interval, 2) for i in range(count)]

    def _normalize_curve(self, values: Sequence[float], target_points: int = 200) -> List[float]:
        if not values:
            return [0.5 for _ in range(target_points)]
        min_val = min(values)
        max_val = max(values)
        normalized = [(v - min_val) / (max_val - min_val + 1e-9) for v in values]
        if len(normalized) == target_points:
            return normalized
        step = max(1, len(normalized) / target_points)
        downsampled = [normalized[int(i * step)] for i in range(target_points)]
        return downsampled

    def _genre_from_tempo(self, tempo: float) -> str:
        if tempo > 130:
            return "electronic"
        if tempo > 110:
            return "pop"
        if tempo > 90:
            return "rnb"
        return "ballad"

    # -------------------------- Lyrics processing ---------------------------
    def auto_format_persian_lyrics(self, lyrics_path: Path) -> List[str]:
        text = lyrics_path.read_text(encoding="utf-8").splitlines()
        cleaned_lines: List[str] = []
        for line in text:
            stripped = line.strip()
            if stripped:
                cleaned_lines.extend(self._auto_break_line(stripped))
        return cleaned_lines

    def _auto_break_line(self, line: str, max_chars: int = 32) -> List[str]:
        if len(line) <= max_chars:
            return [self._apply_rtl(line)]
        words = line.split()
        bucket: List[str] = []
        lines: List[str] = []
        for word in words:
            if sum(len(w) for w in bucket) + len(bucket) + len(word) > max_chars:
                lines.append(self._apply_rtl(" ".join(bucket)))
                bucket = [word]
            else:
                bucket.append(word)
        if bucket:
            lines.append(self._apply_rtl(" ".join(bucket)))
        return lines

    def _apply_rtl(self, line: str) -> str:
        if self._is_persian(line):
            return "".join(reversed(line))
        return line

    def _is_persian(self, line: str) -> bool:
        return bool(re.search(r"[\u0600-\u06FF]", line))

    # -------------------------- Animation directives -----------------------
    def auto_generate_animations(
        self, lines: List[str], analysis: MusicAnalysis, video_path: Path
    ) -> List[AnimationDirective]:
        beats = analysis.beats or [0.0, analysis.duration]
        beat_interval = beats[1] - beats[0] if len(beats) > 1 else 60.0 / analysis.tempo
        palette = self._extract_palette(video_path)

        directives: List[AnimationDirective] = []
        cursor = 0.0
        energy_iter = self._loop_values(analysis.energy, len(lines))
        for idx, line in enumerate(lines):
            duration = max(beat_interval * 2, beat_interval * len(line.split()) * 0.6)
            start = beats[idx] if idx < len(beats) else cursor
            end = start + duration
            emphasis = lines.count(line) > 1
            anchor = "center" if idx % 2 == 0 else "bottom"
            color = self._pick_color(palette, emphasis)
            lyric_line = LyricLine(
                raw_text=line,
                processed_text=line,
                words=line.split(),
                start=start,
                end=end,
                emphasis=emphasis,
                anchor=anchor,
                color=color,
            )
            intensity = next(energy_iter)
            animation_style = self._pick_animation_style(analysis.genre_hint, intensity)
            directives.append(AnimationDirective(line=lyric_line, animation_style=animation_style, intensity=intensity))
            cursor = end
        return directives

    def _loop_values(self, values: Sequence[float], length: int) -> Iterable[float]:
        if not values:
            for _ in range(length):
                yield 0.5
        else:
            idx = 0
            for _ in range(length):
                yield values[idx % len(values)]
                idx += 1

    def _pick_animation_style(self, genre: str, intensity: float) -> str:
        if genre == "electronic":
            return "flash" if intensity > 0.6 else "slide"
        if genre == "pop":
            return "rise" if intensity > 0.5 else "fade"
        if genre == "rnb":
            return "drift" if intensity > 0.5 else "soft-fade"
        return "slow-fade"

    def _extract_palette(self, video_path: Path) -> ColorPalette:
        if video_path in self.palette_cache:
            return self.palette_cache[video_path]
        if PIL_AVAILABLE and video_path.exists():
            with Image.open(video_path) as img:
                resized = img.resize((8, 8))
                colors = resized.convert("RGB").getdata()
                avg = tuple(sum(channel) / len(colors) for channel in zip(*colors))
                primary = self._rgb_to_hex(avg)
                secondary = self._rgb_to_hex((avg[0] * 0.8, avg[1] * 0.8, avg[2] * 0.9))
                accent = self._rgb_to_hex((255 - avg[0], 255 - avg[1], 255 - avg[2]))
                palette = ColorPalette(primary=primary, secondary=secondary, accent=accent)
        else:
            palette = ColorPalette("#d5c4a1", "#83a598", "#fb4934")
        self.palette_cache[video_path] = palette
        return palette

    def _pick_color(self, palette: ColorPalette, emphasis: bool) -> str:
        return palette.accent if emphasis else palette.primary

    def _rgb_to_hex(self, rgb: Sequence[float]) -> str:
        return "#%02x%02x%02x" % tuple(int(min(255, max(0, c))) for c in rgb)

    # -------------------------- Rendering ----------------------------------
    def render_auto_video(
        self,
        directives: List[AnimationDirective],
        video_path: Path,
        music_path: Path,
        analysis: MusicAnalysis,
    ) -> Path:
        output = Path("auto_generated_video.mp4")
        if MANIM_AVAILABLE:
            scene = self._render_with_manim(directives, video_path, music_path, output)
            return scene
        storyboard_path = Path("auto_generated_storyboard.json")
        storyboard_path.write_text(self._serialize_storyboard(directives, analysis), encoding="utf-8")
        return storyboard_path

    def _render_with_manim(
        self,
        directives: List[AnimationDirective],
        video_path: Path,
        music_path: Path,
        output: Path,
    ) -> Path:
        class AutoLyricsScene(Scene):
            def construct(self_inner) -> None:
                palette = self._extract_palette(video_path)
                text_group = VGroup()
                for directive in directives:
                    color = rgb_to_color(self._hex_to_rgb_tuple(directive.line.color))
                    text = Text(
                        directive.line.processed_text,
                        color=color,
                        font_size=self._font_size_from_video(video_path),
                    )
                    self_inner._position_text(text, directive.line.anchor)
                    text_group.add(text)
                self_inner.add_sound(str(music_path))
                for directive, text in zip(directives, text_group):
                    duration = max(0.5, directive.line.end - directive.line.start)
                    if directive.animation_style in {"fade", "soft-fade", "slow-fade"}:
                        self_inner.play(FadeIn(text, run_time=0.4))
                        self_inner.wait(duration)
                        self_inner.play(FadeOut(text, run_time=0.4))
                    elif directive.animation_style in {"slide", "rise"}:
                        self_inner.play(text.animate.shift(RIGHT * 0.5), run_time=0.4)
                        self_inner.wait(duration)
                        self_inner.play(text.animate.shift(-RIGHT * 0.5), run_time=0.3)
                    else:
                        self_inner.play(FadeIn(text, run_time=0.2))
                        self_inner.wait(duration)
                        self_inner.play(FadeOut(text, run_time=0.2))

            def _position_text(self_inner, text: Text, anchor: str) -> None:
                if anchor == "bottom":
                    text.to_edge(direction=DOWN)
                elif anchor == "center":
                    text.move_to(ORIGIN)
                else:
                    text.to_edge(direction=ORIGIN)

        scene = AutoLyricsScene()
        scene.render(file_name=str(output))
        return output

    def _hex_to_rgb_tuple(self, hex_color: str) -> tuple[int, int, int]:
        hex_value = hex_color.lstrip("#")
        return tuple(int(hex_value[i : i + 2], 16) for i in (0, 2, 4))

    def _font_size_from_video(self, video_path: Path) -> int:
        if PIL_AVAILABLE and video_path.exists():
            with Image.open(video_path) as img:
                base = max(img.size) / 20
                return int(max(24, min(72, base)))
        return 48

    def _serialize_storyboard(self, directives: List[AnimationDirective], analysis: MusicAnalysis) -> str:
        data = {
            "analysis": dataclasses.asdict(analysis),
            "timeline": [
                {
                    "text": directive.line.processed_text,
                    "start": directive.line.start,
                    "end": directive.line.end,
                    "style": directive.animation_style,
                    "color": directive.line.color,
                    "anchor": directive.line.anchor,
                }
                for directive in directives
            ],
        }
        return json.dumps(data, ensure_ascii=False, indent=2)


# -------------------------- CLI -------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automatically render a Persian lyric video with Manim.")
    parser.add_argument("--lyrics", required=True, help="Path to the lyrics text file.")
    parser.add_argument("--music", required=True, help="Path to the music file (mp3/wav).")
    parser.add_argument("--video", required=True, help="Path to the background video file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generator = AutoMusicVideoGenerator()
    output = generator.process_all_inputs(args.lyrics, args.music, args.video)
    print(f"✅ Video created automatically at {output}!")


if __name__ == "__main__":
    main()
