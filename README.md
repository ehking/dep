# Automated Persian Lyric Video Generator

This repository provides a fully automated pipeline for generating motion-graphics lyric videos with [Manim](https://www.manim.community/). Supply a Persian lyrics file, a music track, and a background video, then run a single command to produce a synchronized export or a storyboard when Manim is unavailable.

## Quick start

```bash
python auto_music_video.py --lyrics lyrics.txt --music song.mp3 --video background.mp4
```

The script will:
- Detect Persian lyrics and apply RTL rendering.
- Analyze the music file to estimate tempo, beats, and energy.
- Distribute lyrics across the detected beats.
- Choose animation styles and color palettes automatically.
- Render a Manim video (or emit a JSON storyboard if Manim is not installed).

## Implementation notes
- Uses `librosa`/`pydub` for audio analysis when available, with graceful fallbacks.
- Automatically samples a color palette from the background video when `Pillow` is installed.
- Exposes a single class, `AutoMusicVideoGenerator`, which wraps the entire automated workflow.
