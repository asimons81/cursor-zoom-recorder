import os
import time
import threading
import shutil
from dataclasses import dataclass

import cv2
import numpy as np
import mss
from pynput import mouse


@dataclass
class RecorderConfig:
    mode: str  # 'always', 'click', 'smart'
    zoom: float = 2.0
    fps: int = 30
    output_dir: str = None
    output_gif: bool = False
    highlight: bool = True
    capture_rect: tuple = None  # (left, top, width, height)


class CursorZoomRecorder:
    def __init__(self, config: RecorderConfig):
        self.config = config
        self._running = False
        self._thread = None
        self._mouse_listener = None
        self._cursor_pos = (0, 0)
        self._mouse_down = False
        self._last_pos = (0, 0)
        self._last_ts = time.time()
        self._ripple_events = []  # list of (x, y, t0)

    def start(self):
        if self._running:
            return
        self._running = True
        self._start_mouse_listener()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._mouse_listener:
            self._mouse_listener.stop()
        if self._thread:
            self._thread.join(timeout=2)

    def _start_mouse_listener(self):
        def on_move(x, y):
            self._cursor_pos = (x, y)

        def on_click(x, y, button, pressed):
            self._mouse_down = pressed
            if pressed:
                self._ripple_events.append((x, y, time.time()))

        self._mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
        self._mouse_listener.start()

    def _should_zoom(self):
        if self.config.mode == 'always':
            return True
        if self.config.mode == 'click':
            return self._mouse_down
        # smart: zoom when cursor slows
        now = time.time()
        dx = self._cursor_pos[0] - self._last_pos[0]
        dy = self._cursor_pos[1] - self._last_pos[1]
        dt = max(1e-3, now - self._last_ts)
        speed = (dx * dx + dy * dy) ** 0.5 / dt
        self._last_pos = self._cursor_pos
        self._last_ts = now
        return speed < 250  # px/s threshold

    def _draw_cursor_effects(self, frame):
        x, y = self._cursor_pos
        h, w = frame.shape[:2]
        if 0 <= x < w and 0 <= y < h:
            if self.config.highlight:
                cv2.circle(frame, (x, y), 12, (0, 180, 255), 2)
        # ripple effects
        now = time.time()
        new_events = []
        for rx, ry, t0 in self._ripple_events:
            age = now - t0
            if age > 0.6:
                continue
            radius = int(20 + age * 80)
            alpha = max(0, 1 - age / 0.6)
            overlay = frame.copy()
            cv2.circle(overlay, (rx, ry), radius, (255, 255, 255), 2)
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
            new_events.append((rx, ry, t0))
        self._ripple_events = new_events

    def _zoom_frame(self, frame, cursor, zoom):
        h, w = frame.shape[:2]
        zx = int(w / zoom)
        zy = int(h / zoom)
        cx, cy = cursor
        x1 = max(0, min(w - zx, int(cx - zx / 2)))
        y1 = max(0, min(h - zy, int(cy - zy / 2)))
        crop = frame[y1:y1 + zy, x1:x1 + zx]
        return cv2.resize(crop, (w, h), interpolation=cv2.INTER_LINEAR)

    def _run(self):
        output_dir = self.config.output_dir or os.path.join(os.path.expanduser("~"), "Videos", "ZoomedRecordings")
        os.makedirs(output_dir, exist_ok=True)
        ts = time.strftime("%Y%m%d-%H%M%S")
        mp4_path = os.path.join(output_dir, f"recording-{ts}.mp4")
        gif_path = os.path.join(output_dir, f"recording-{ts}.gif")

        with mss.mss() as sct:
            if self.config.capture_rect:
                left, top, width, height = self.config.capture_rect
                monitor = {"left": left, "top": top, "width": width, "height": height}
            else:
                monitor = sct.monitors[1]
                width = monitor['width']
                height = monitor['height']

            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(mp4_path, fourcc, self.config.fps, (width, height))

            frame_interval = 1.0 / self.config.fps
            last_frame_time = time.time()

            while self._running:
                now = time.time()
                if now - last_frame_time < frame_interval:
                    time.sleep(0.001)
                    continue
                last_frame_time = now

                img = np.array(sct.grab(monitor))
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

                if self._should_zoom():
                    frame = self._zoom_frame(frame, self._cursor_pos, self.config.zoom)

                self._draw_cursor_effects(frame)
                writer.write(frame)

            writer.release()

        if self.config.output_gif and shutil.which("ffmpeg"):
            cmd = f'ffmpeg -y -i "{mp4_path}" -vf "fps=12,scale=960:-1:flags=lanczos" "{gif_path}"'
            os.system(cmd)

        self._running = False
