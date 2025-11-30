# استودیو موشن گرافیک تحت وب

یک نمونهٔ رابط کاربری فارسی برای ساخت موشن گرافیک پیشرفته با الگوهای آماده، پیش‌نمایش زنده، افکت‌های متن، همگام‌سازی صوت و گزینه‌های خروجی حرفه‌ای.

## اجرای سریع
```bash
python dev_server.py --port 8000
# Automated Persian Lyric Video Generator

This repository provides a fully automated pipeline for generating motion-graphics lyric videos with [Manim](https://www.manim.community/). Supply a Persian lyrics file, a music track, and a background video, then run a single command to produce a synchronized export or a storyboard when Manim is unavailable.

## Quick start

```bash
python auto_music_video.py --lyrics lyrics.txt --music song.mp3 --video background.mp4
```
سپس در مرورگر به نشانی `http://localhost:8000` بروید. اگر مرورگر شما به‌صورت خودکار تلاش کرد با HTTPS به درگاه ۸۰۰۰ متصل شود و پیام «Bad request version» ظاهر شد، از همین اسکریپت `dev_server.py` استفاده کنید؛ این اسکریپت درخواست‌های TLS اشتباه را تشخیص داده و بدون تولید خطای ۴۰۰، پیام راهنما در لاگ ثبت می‌کند.

### رفع خطای «Bad request version» مربوط به TLS

این خطا زمانی رخ می‌دهد که یک سرویس یا افزونهٔ مرورگر تلاش می‌کند اتصال HTTPS برقرار کند، درحالی‌که سرور شما فقط HTTP ساده را می‌شنود. برای برطرف‌کردن آن:

1. **تنظیمات سرور را بررسی کنید.**
   - اگر از جنگو استفاده می‌کنید، مطمئن شوید در محیط توسعه از گزینهٔ `--ssl` استفاده نکرده‌اید.
   - اگر از فلاسک استفاده می‌کنید، پارامتر `ssl_context='adhoc'` را حذف کنید تا سرور به‌صورت HTTP اجرا شود.
   - اگر از `python -m http.server` یا سرور ساده استفاده می‌کنید، روی پورتی که برای HTTP درنظر گرفته‌اید (مثلاً ۸۰۰۰) اجرا کنید و به همان نشانی با `http://` متصل شوید.

2. **نمونهٔ صحیح اجرای جنگو در توسعه:**

```bash
# نادرست
python manage.py runserver --ssl

# درست
python manage.py runserver 127.0.0.1:8000
```

اگر همچنان درخواست اشتباهی به درگاه HTTP فرستاده می‌شود، `dev_server.py` را اجرا کنید تا دست‌دهی‌های TLS نادرست را تشخیص دهد و پیام راهنمای «use https:// or plain http://» در لاگ درج کند، بدون اینکه لاگ شما از خطاهای ۴۰۰ پر شود.

## قابلیت‌های کلیدی
- الگوهای آماده، اعمال یک‌کلیکی و ذخیرهٔ الگوی شخصی.
- پیش‌نمایش زنده با تایم‌لاین صحنه، حالت کم‌کیفیت/پرتوان، و انیمیشن فوری.
- افکت‌های متن شامل خوشنویسی فارسی، متن روی مسیر منحنی، چرخش سه‌بعدی، و گرادیان رنگی.
- ادغام صدا: بارگذاری موسیقی، همگام‌سازی صداگذاری و نمایش موج.
- خروجی حرفه‌ای: پردازش دسته‌ای، رندر ابری شبیه‌سازی‌شده، و پروفایل شبکه‌های اجتماعی.
- پیام‌های خطای دوستانه به فارسی، فانت‌های جایگزین و بررسی سازگاری فرمت.
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
