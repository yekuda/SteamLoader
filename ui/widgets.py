from PySide6.QtWidgets import QLabel, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# Stil tanımlarını style.py dosyasından içe aktar
from ui.style import DRAG_DROP_AREA_STYLE

# PySide6 sabitlerini doğrudan içe aktar
AlignCenter = Qt.AlignCenter
LeftButton = Qt.LeftButton

class DragDropLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText('Oyun dosyasını buraya sürükleyin veya seçin')
        self.setAlignment(AlignCenter)
        self.setStyleSheet(DRAG_DROP_AREA_STYLE)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        from ui.style import DRAG_DROP_HOVER_STYLE
        if event.mimeData().hasUrls():
            self.setStyleSheet(DRAG_DROP_AREA_STYLE + DRAG_DROP_HOVER_STYLE)
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet(DRAG_DROP_AREA_STYLE)

    def dropEvent(self, event):
        self.setStyleSheet(DRAG_DROP_AREA_STYLE)
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().endswith('.zip'):
                    self.parent().process_zip(url.toLocalFile())

    def mousePressEvent(self, event):
        if event.button() == LeftButton:
            self.parent().select_zip_file()