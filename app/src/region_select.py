from PySide6.QtWidgets import QDialog, QRubberBand
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QGuiApplication


class RegionSelectDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setWindowState(Qt.WindowFullScreen)
        self.setWindowOpacity(0.25)
        self.rubber = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()
        self.selection = None

    def mousePressEvent(self, event):
        self.origin = event.pos()
        self.rubber.setGeometry(QRect(self.origin, self.origin))
        self.rubber.show()

    def mouseMoveEvent(self, event):
        self.rubber.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        rect = self.rubber.geometry()
        self.rubber.hide()
        self.selection = rect
        self.accept()


def select_region():
    dlg = RegionSelectDialog()
    dlg.exec()
    if not dlg.selection:
        return None

    # Map to global screen coordinates
    screen = QGuiApplication.primaryScreen()
    geo = screen.geometry()
    rect = dlg.selection
    return (geo.x() + rect.x(), geo.y() + rect.y(), rect.width(), rect.height())
