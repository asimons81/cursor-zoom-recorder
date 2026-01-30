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
- Current capture: full screen. Window/region selection coming next.
