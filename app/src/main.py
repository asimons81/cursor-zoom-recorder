import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QHBoxLayout, QSpinBox, QDoubleSpinBox, QMessageBox, QInputDialog
from PySide6.QtCore import Qt

from recorder import RecorderConfig, CursorZoomRecorder
from region_select import select_region
from capture import list_windows, get_window_rect
from hotkeys import HotkeyManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cursor Zoom Recorder")
        self.setMinimumSize(720, 420)
        self.recorder = None
        self.capture_rect = None
        self.hotkeys = HotkeyManager(self.start_recording, self.stop_recording, self.toggle_pause)
        self.hotkeys.start()

        root = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Cursor Zoom Recorder")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")

        capture_row = QHBoxLayout()
        capture_row.addWidget(QLabel("Capture:"))
        self.capture_combo = QComboBox()
        self.capture_combo.addItems(["Full Screen", "Window", "Region"])
        capture_row.addWidget(self.capture_combo)
        self.capture_combo.currentTextChanged.connect(self.on_capture_changed)
        capture_row.addStretch()

        zoom_row = QHBoxLayout()
        zoom_row.addWidget(QLabel("Zoom mode:"))
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["Always follow", "Click+drag", "Smart (slow-down)"])
        zoom_row.addWidget(self.zoom_combo)

        zoom_row.addWidget(QLabel("Zoom:"))
        self.zoom_spin = QDoubleSpinBox()
        self.zoom_spin.setRange(1.0, 4.0)
        self.zoom_spin.setSingleStep(0.25)
        self.zoom_spin.setValue(2.0)
        zoom_row.addWidget(self.zoom_spin)
        zoom_row.addStretch()

        output_row = QHBoxLayout()
        output_row.addWidget(QLabel("Output:"))
        self.output_combo = QComboBox()
        self.output_combo.addItems(["MP4", "MP4 + GIF"])
        output_row.addWidget(self.output_combo)

        output_row.addWidget(QLabel("FPS:"))
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(10, 60)
        self.fps_spin.setValue(30)
        output_row.addWidget(self.fps_spin)
        output_row.addStretch()

        self.status = QLabel("Status: idle")
        self.status.setStyleSheet("color: #999;")

        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")
        self.pause_btn = QPushButton("Pause")
        self.stop_btn.setEnabled(False)
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.pause_btn)
        btn_row.addWidget(self.stop_btn)
        btn_row.addStretch()

        self.start_btn.clicked.connect(self.start_recording)
        self.stop_btn.clicked.connect(self.stop_recording)
        self.pause_btn.clicked.connect(self.toggle_pause)

        layout.addWidget(title)
        layout.addLayout(capture_row)
        layout.addLayout(zoom_row)
        layout.addLayout(output_row)
        layout.addWidget(self.status)
        layout.addLayout(btn_row)
        layout.addStretch()

        root.setLayout(layout)
        self.setCentralWidget(root)

    def on_capture_changed(self, value):
        if value == "Region":
            rect = select_region()
            self.capture_rect = rect
            if rect:
                self.status.setText(f"Status: region set {rect}")
        elif value == "Window":
            windows = list_windows()
            if not windows:
                QMessageBox.information(self, "No windows", "No windows detected or pywin32 not available.")
                self.capture_rect = None
                return
            titles = [t for t, _ in windows]
            title, ok = QInputDialog.getItem(self, "Select window", "Window:", titles, 0, False)
            if ok and title:
                rect = get_window_rect(title)
                if rect:
                    left, top, right, bottom = rect
                    self.capture_rect = (left, top, right - left, bottom - top)
                    self.status.setText(f"Status: window set {title}")
        else:
            self.capture_rect = None
            self.status.setText("Status: idle")

    def start_recording(self):
        if self.recorder:
            return
        mode_map = {
            "Always follow": "always",
            "Click+drag": "click",
            "Smart (slow-down)": "smart",
        }
        cfg = RecorderConfig(
            mode=mode_map[self.zoom_combo.currentText()],
            zoom=float(self.zoom_spin.value()),
            fps=int(self.fps_spin.value()),
            output_gif=self.output_combo.currentText() == "MP4 + GIF",
            capture_rect=self.capture_rect,
        )

        if self.capture_combo.currentText() != "Full Screen" and not self.capture_rect:
            QMessageBox.information(self, "Pick a target", "Select a window or region first.")
            return

        self.recorder = CursorZoomRecorder(cfg)
        self.recorder.start()
        self.status.setText("Status: recording")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop_recording(self):
        if not self.recorder:
            return
        self.recorder.stop()
        self.recorder = None
        out_dir = os.path.join(os.path.expanduser("~"), "Videos", "ZoomedRecordings")
        self.status.setText(f"Status: saved to {out_dir}")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def toggle_pause(self):
        if self.recorder:
            self.recorder.toggle_pause()
            self.status.setText("Status: paused" if self.recorder._paused else "Status: recording")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
