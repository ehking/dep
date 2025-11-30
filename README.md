# Persian Motion Graphics Creator

A Tkinter-based GUI that wires together Persian text processing, video selection, and Manim Community Edition rendering to create RTL-friendly motion graphics.

## Features
- Persian text entry with automatic RTL reshaping (arabic_reshaper + python-bidi)
- Font, size, color, and animation selectors with live preview canvas
- Video background picker with trim and volume controls
- Timeline controls for text duration and transition styles
- Export tab for resolution, FPS, and format selection, plus progress feedback
- Project save/load to JSON for quick iteration
- Threaded render manager scaffolded for Manim CE scenes

## Running the app
```bash
pip install manim arabic-reshaper python-bidi
python app.py
```

Rendering is invoked asynchronously; the heavy `scene.render()` call is commented for sandbox environments but wired for real projects.
