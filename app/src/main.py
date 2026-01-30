import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QHBoxLayout, QSpinBox, QDoubleSpinBox, QMessageBox
from PySide6.QtCore import Qt

from recorder import RecorderConfig, CursorZoomRecorder


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cursor Zoom Recorder")
        self.setMinimumSize(720, 420)
        self.recorder = None

        root = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Cursor Zoom Recorder")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")

        capture_row = QHBoxLayout()
        capture_row.addWidget(QLabel("Capture:"))
        self.capture_combo = QComboBox()
        self.capture_combo.addItems(["Full Screen", "Window", "Region"])
        capture_row.addWidget(self.capture_combo)
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
        self.stop_btn.setEnabled(False)
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.stop_btn)
        btn_row.addStretch()

        self.start_btn.clicked.connect(self.start_recording)
        self.stop_btn.clicked.connect(self.stop_recording)

        layout.addWidget(title)
        layout.addLayout(capture_row)
        layout.addLayout(zoom_row)
        layout.addLayout(output_row)
        layout.addWidget(self.status)
        layout.addLayout(btn_row)
        layout.addStretch()

        root.setLayout(layout)
        self.setCentralWidget(root)

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
        )

        if self.capture_combo.currentText() != "Full Screen":
            QMessageBox.information(self, "Not yet", "Window/Region capture is coming next. Full screen works now.")

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
