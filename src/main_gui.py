"""Tkinter GUI for the Persian Motion Graphics Creator."""

import json
import logging
from pathlib import Path
from tkinter import (  # noqa: WPS347
    BOTH,
    END,
    HORIZONTAL,
    LEFT,
    RIGHT,
    Button,
    Canvas,
    Entry,
    Frame,
    Label,
    Scale,
    StringVar,
    Text,
    Tk,
)
from tkinter import colorchooser, filedialog, ttk

from .config import DefaultConfig, ResolutionSetting, load_default_config
from .logger_setup import configure_logging
from .render_manager import RenderManager
from .scene_composer import SceneComposer, SceneConfig
from .text_animator import AnimatedText, PersianTextAnimator
from .video_processor import VideoProcessor

logger = logging.getLogger(__name__)


class MainGUI:
    """Primary window with tabs for text, video, animation, and export settings."""

    def __init__(self) -> None:
        configure_logging()
        self.config: DefaultConfig = load_default_config()
        self.window = Tk()
        self.window.title("Persian Motion Graphics Creator")
        self.window.geometry("1200x800")

        self.text_animator = PersianTextAnimator(default_font=self.config.fonts[0])
        self.video_processor = VideoProcessor()
        self.selected_resolution: ResolutionSetting = self.config.resolutions[1]
        self.selected_fps: int = self.config.fps_options[0]
        self.selected_format: StringVar = StringVar(value=self.config.output_formats[0])
        self.progress_var = StringVar(value="0%")
        self.status_var = StringVar(value="آماده")
        self.text_color_var = StringVar(value="#ffffff")

        self._build_layout()
        self._setup_renderer()

    def _build_layout(self) -> None:
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=BOTH, expand=True)

        self.text_tab = Frame(notebook)
        self.video_tab = Frame(notebook)
        self.animation_tab = Frame(notebook)
        self.export_tab = Frame(notebook)

        notebook.add(self.text_tab, text="متن")
        notebook.add(self.video_tab, text="ویدیو")
        notebook.add(self.animation_tab, text="انیمیشن")
        notebook.add(self.export_tab, text="خروجی")

        self._build_text_tab()
        self._build_video_tab()
        self._build_animation_tab()
        self._build_export_tab()

    def _build_text_tab(self) -> None:
        Label(self.text_tab, text="عنوان:").pack(anchor="w", padx=10, pady=5)
        self.title_input = Entry(self.text_tab, font=("Arial", 14))
        self.title_input.pack(fill="x", padx=10)
        self.title_input.insert(0, "عنوان پروژه")

        Label(self.text_tab, text="متن:").pack(anchor="w", padx=10, pady=5)
        self.body_input = Text(self.text_tab, height=8, font=("Arial", 12))
        self.body_input.pack(fill=BOTH, padx=10, pady=5)
        self.body_input.insert(END, self.config.sample_text)

        font_frame = Frame(self.text_tab)
        font_frame.pack(fill="x", padx=10, pady=5)
        Label(font_frame, text="فونت:").pack(side=LEFT)
        self.font_var = StringVar(value=self.config.fonts[0])
        font_dropdown = ttk.Combobox(font_frame, textvariable=self.font_var, values=self.config.fonts)
        font_dropdown.pack(side=LEFT)

        Label(font_frame, text="حجم فونت:").pack(side=LEFT, padx=10)
        self.size_var = StringVar(value="36")
        size_dropdown = ttk.Combobox(font_frame, textvariable=self.size_var, values=["24", "32", "36", "48", "60"])
        size_dropdown.pack(side=LEFT)

        Label(font_frame, text="جلوه:").pack(side=LEFT, padx=10)
        self.animation_style_var = StringVar(value=list(self.config.animation_styles.keys())[0])
        animation_dropdown = ttk.Combobox(
            font_frame,
            textvariable=self.animation_style_var,
            values=list(self.config.animation_styles.keys()),
        )
        animation_dropdown.pack(side=LEFT)

        Label(font_frame, text="رنگ:").pack(side=LEFT, padx=10)
        color_preview = Label(font_frame, width=3, bg=self.text_color_var.get())
        color_preview.pack(side=LEFT)
        Button(font_frame, text="انتخاب رنگ", command=lambda: self._choose_color(color_preview)).pack(side=LEFT, padx=5)

        self.preview_canvas = Canvas(self.text_tab, height=120, bg="#f2f2f2")
        self.preview_canvas.pack(fill="x", padx=10, pady=10)
        self.preview_canvas.create_text(
            580,
            60,
            text=self.text_animator.reshape_text(self.config.sample_text),
            font=(self.font_var.get(), 20),
            fill=self.text_color_var.get(),
        )

        self.body_input.bind("<KeyRelease>", lambda _event: self._refresh_text_preview())
        self.font_var.trace_add("write", lambda *_: self._refresh_text_preview())
        self.size_var.trace_add("write", lambda *_: self._refresh_text_preview())

    def _choose_color(self, preview_label: Label) -> None:
        color = colorchooser.askcolor(initialcolor=self.text_color_var.get())
        if color and color[1]:
            self.text_color_var.set(color[1])
            preview_label.configure(bg=color[1])
            self._refresh_text_preview()

    def _refresh_text_preview(self) -> None:
        self.preview_canvas.delete("all")
        reshaped_title = self.text_animator.reshape_text(self.title_input.get())
        reshaped_body = self.text_animator.reshape_text(self.body_input.get("1.0", END))
        self.preview_canvas.create_text(
            580,
            40,
            text=reshaped_title,
            font=(self.font_var.get(), int(self.size_var.get())),
            fill=self.text_color_var.get(),
        )
        self.preview_canvas.create_text(
            580,
            90,
            text=reshaped_body,
            font=(self.font_var.get(), max(16, int(self.size_var.get()) - 4)),
            fill=self.text_color_var.get(),
        )

    def _build_video_tab(self) -> None:
        file_frame = Frame(self.video_tab)
        file_frame.pack(fill="x", padx=10, pady=5)
        Label(file_frame, text="فایل ویدیو:").pack(side=LEFT)
        self.video_path_var = StringVar()
        Entry(file_frame, textvariable=self.video_path_var).pack(side=LEFT, fill="x", expand=True, padx=5)
        Button(file_frame, text="انتخاب", command=self._browse_video).pack(side=LEFT)

        preview_frame = Frame(self.video_tab, bd=2, relief="groove")
        preview_frame.pack(fill="both", padx=10, pady=5, expand=True)
        Label(preview_frame, text="پیش‌نمایش ویدیو (نمونه)").pack()
        self.video_preview = Canvas(preview_frame, bg="#000", height=240)
        self.video_preview.pack(fill="both", expand=True, padx=10, pady=10)

        control_frame = Frame(self.video_tab)
        control_frame.pack(fill="x", padx=10, pady=5)
        Label(control_frame, text="حجم صدا:").pack(side=LEFT)
        self.volume_slider = Scale(control_frame, from_=0, to=1, resolution=0.05, orient=HORIZONTAL, command=self._on_volume_change)
        self.volume_slider.set(1)
        self.volume_slider.pack(side=LEFT)

        Label(control_frame, text="شروع (ثانیه):").pack(side=LEFT, padx=10)
        self.start_time = Scale(control_frame, from_=0, to=60, orient=HORIZONTAL, command=self._on_trim_change)
        self.start_time.pack(side=LEFT, fill="x", expand=True)

        Label(control_frame, text="پایان (ثانیه):").pack(side=LEFT, padx=10)
        self.end_time = Scale(control_frame, from_=0, to=60, orient=HORIZONTAL, command=self._on_trim_change)
        self.end_time.set(10)
        self.end_time.pack(side=LEFT, fill="x", expand=True)

    def _build_animation_tab(self) -> None:
        Label(self.animation_tab, text="طول نمایش متن (ثانیه)").pack(anchor="w", padx=10, pady=5)
        self.duration_slider = Scale(self.animation_tab, from_=1, to=10, orient=HORIZONTAL)
        self.duration_slider.set(4)
        self.duration_slider.pack(fill="x", padx=10)

        Label(self.animation_tab, text="افکت انتقال").pack(anchor="w", padx=10, pady=5)
        self.transition_var = StringVar(value=self.config.transition_styles[0])
        transition_dropdown = ttk.Combobox(self.animation_tab, textvariable=self.transition_var, values=self.config.transition_styles)
        transition_dropdown.pack(fill="x", padx=10)

        order_frame = Frame(self.animation_tab)
        order_frame.pack(fill="both", expand=True, padx=10, pady=10)
        Label(order_frame, text="ترتیب صحنه‌ها (نمونه)").pack(anchor="w")
        self.scene_order = Text(order_frame, height=6)
        self.scene_order.pack(fill="both", expand=True)
        self.scene_order.insert(END, "۱. عنوان\n۲. متن اصلی\n۳. پایان")

    def _build_export_tab(self) -> None:
        res_frame = Frame(self.export_tab)
        res_frame.pack(fill="x", padx=10, pady=5)
        Label(res_frame, text="وضوح:").pack(side=LEFT)
        res_values = [res.label for res in self.config.resolutions]
        self.resolution_var = StringVar(value=self.selected_resolution.label)
        resolution_dropdown = ttk.Combobox(res_frame, textvariable=self.resolution_var, values=res_values)
        resolution_dropdown.pack(side=LEFT)
        resolution_dropdown.bind("<<ComboboxSelected>>", self._on_resolution_change)

        Label(res_frame, text="فریم بر ثانیه:").pack(side=LEFT, padx=10)
        fps_dropdown = ttk.Combobox(res_frame, values=self.config.fps_options)
        fps_dropdown.set(self.selected_fps)
        fps_dropdown.bind("<<ComboboxSelected>>", self._on_fps_change)
        fps_dropdown.pack(side=LEFT)

        Label(res_frame, text="فرمت خروجی:").pack(side=LEFT, padx=10)
        format_dropdown = ttk.Combobox(res_frame, textvariable=self.selected_format, values=self.config.output_formats)
        format_dropdown.pack(side=LEFT)

        Button(self.export_tab, text="ذخیره پروژه", command=self._save_project).pack(side=LEFT, padx=10, pady=10)
        Button(self.export_tab, text="بارگذاری پروژه", command=self._load_project).pack(side=LEFT, padx=10, pady=10)
        Button(self.export_tab, text="رندر", command=self._start_render).pack(side=RIGHT, padx=10, pady=10)

        self.progress_bar = ttk.Progressbar(self.export_tab, mode="determinate")
        self.progress_bar.pack(fill="x", padx=10, pady=10)
        self.progress_label = Label(self.export_tab, textvariable=self.progress_var)
        self.progress_label.pack(anchor="e", padx=10)
        self.status_label = Label(self.export_tab, textvariable=self.status_var)
        self.status_label.pack(anchor="w", padx=10)

    def _setup_renderer(self) -> None:
        scene_config = SceneConfig(
            width=self.selected_resolution.width,
            height=self.selected_resolution.height,
            fps=self.selected_fps,
        )
        self.composer = SceneComposer(config=scene_config)
        self.render_manager = RenderManager(
            composer=self.composer,
            output_dir=Path("output"),
            progress_callback=self._on_render_progress,
            completion_callback=self._on_render_complete,
        )

    def _browse_video(self) -> None:
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.mov *.avi")])
        if file_path:
            self.video_path_var.set(file_path)
            try:
                self.video_processor.select_file(file_path)
                self.status_var.set("ویدیو انتخاب شد")
            except FileNotFoundError as exc:
                self.status_var.set(str(exc))

    def _on_volume_change(self, value: str) -> None:
        self.video_processor.set_volume(float(value))

    def _on_trim_change(self, _value: str) -> None:
        self.video_processor.update_trim(float(self.start_time.get()), float(self.end_time.get()))

    def _on_resolution_change(self, _event: object) -> None:
        selected_label = self.resolution_var.get()
        for res in self.config.resolutions:
            if res.label == selected_label:
                self.selected_resolution = res
                break
        self._setup_renderer()

    def _on_fps_change(self, event: object) -> None:  # noqa: ARG002 - tkinter protocol
        self.selected_fps = int(event.widget.get())
        self._setup_renderer()

    def _save_project(self) -> None:
        project = self._collect_state()
        path = Path(f"projects/{project['title']}.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(project, ensure_ascii=False, indent=2))
        self.status_var.set(f"پروژه ذخیره شد: {path}")

    def _load_project(self) -> None:
        file_path = filedialog.askopenfilename(filetypes=[("Project", "*.json")])
        if not file_path:
            return
        data = json.loads(Path(file_path).read_text())
        self._apply_state(data)
        self.status_var.set("پروژه بارگذاری شد")

    def _collect_state(self) -> dict:
        return {
            "title": self.title_input.get(),
            "body": self.body_input.get("1.0", END).strip(),
            "font": self.font_var.get(),
            "size": int(self.size_var.get()),
            "animation": self.animation_style_var.get(),
            "duration": float(self.duration_slider.get()),
            "transition": self.transition_var.get(),
            "resolution": self.selected_resolution.label,
            "fps": self.selected_fps,
            "format": self.selected_format.get(),
            "video": {
                "path": str(self.video_processor.selection.path) if self.video_processor.selection.path else "",
                "start": self.video_processor.selection.start_time,
                "end": self.video_processor.selection.end_time,
                "volume": self.video_processor.selection.volume,
            },
        }

    def _apply_state(self, data: dict) -> None:
        self.title_input.delete(0, END)
        self.title_input.insert(0, data.get("title", ""))
        self.body_input.delete("1.0", END)
        self.body_input.insert(END, data.get("body", ""))
        self.font_var.set(data.get("font", self.config.fonts[0]))
        self.size_var.set(str(data.get("size", 36)))
        self.animation_style_var.set(data.get("animation", list(self.config.animation_styles.keys())[0]))
        self.duration_slider.set(data.get("duration", 4))
        self.transition_var.set(data.get("transition", self.config.transition_styles[0]))
        self.resolution_var.set(data.get("resolution", self.config.resolutions[0].label))
        self.selected_format.set(data.get("format", self.config.output_formats[0]))
        self.selected_fps = int(data.get("fps", self.config.fps_options[0]))
        video_info = data.get("video", {})
        if video_info.get("path"):
            try:
                self.video_processor.select_file(video_info["path"])
                self.video_path_var.set(video_info["path"])
            except FileNotFoundError:
                self.status_var.set("فایل ویدیو یافت نشد")
        self.video_processor.update_trim(video_info.get("start", 0.0), video_info.get("end", 0.0))
        self.volume_slider.set(video_info.get("volume", 1.0))

    def _start_render(self) -> None:
        texts = self.text_animator.build_animated_sequence(
            [
                AnimatedText(
                    content=self.title_input.get(),
                    font=self.font_var.get(),
                    color=self.text_color_var.get(),
                    size=int(self.size_var.get()),
                    animation=self.animation_style_var.get(),
                    duration=float(self.duration_slider.get()),
                ),
                AnimatedText(
                    content=self.body_input.get("1.0", END),
                    font=self.font_var.get(),
                    color=self.text_color_var.get(),
                    size=int(self.size_var.get()) - 4,
                    animation=self.animation_style_var.get(),
                    duration=float(self.duration_slider.get()),
                ),
            ]
        )
        self.progress_var.set("0%")
        self.progress_bar['value'] = 0
        self.render_manager.render_async(texts)
        self.status_var.set("در حال رندر...")

    def _on_render_progress(self, value: float) -> None:
        percent = int(value * 100)
        self.progress_bar['value'] = percent
        self.progress_var.set(f"{percent}%")

    def _on_render_complete(self, output: Path) -> None:
        self.status_var.set(f"رندر کامل شد: {output}")

    def run(self) -> None:
        self.window.mainloop()


def main() -> None:
    gui = MainGUI()
    gui.run()


if __name__ == "__main__":
    main()
