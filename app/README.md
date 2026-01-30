# App (Windows)

## Setup
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

## Notes
- FFmpeg required for GIF output (MP4 works without it).
- Capture supports full screen, window, or region (Windows; requires pywin32).

## Hotkeys
- Start: Ctrl+Shift+R
- Stop: Ctrl+Shift+S
- Pause: Ctrl+Shift+P

## Build Windows EXE
```bash
pip install -r requirements.txt
cd installer
pyinstaller pyinstaller.spec
```
