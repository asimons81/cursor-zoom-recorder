import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QHBoxLayout
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cursor Zoom Recorder")
        self.setMinimumSize(720, 420)

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
        zoom_row.addStretch()

        output_row = QHBoxLayout()
        output_row.addWidget(QLabel("Output:"))
        self.output_combo = QComboBox()
        self.output_combo.addItems(["MP4", "MP4 + GIF"])
        output_row.addWidget(self.output_combo)
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

        layout.addWidget(title)
        layout.addLayout(capture_row)
        layout.addLayout(zoom_row)
        layout.addLayout(output_row)
        layout.addWidget(self.status)
        layout.addLayout(btn_row)
        layout.addStretch()

        root.setLayout(layout)
        self.setCentralWidget(root)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
