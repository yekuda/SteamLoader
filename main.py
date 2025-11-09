import sys
import os

# Python bytecode oluşturmayı engelle
sys.dont_write_bytecode = True

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QIcon

# Uygulamanın ana penceresini main_window.py dosyasından içe aktar
from main_window import SteamUploader

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    font = QFont('Segoe UI')
    app.setFont(font)
    
    icon_path = resource_path('favicon.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        
    window = SteamUploader()
    window.show()
    sys.exit(app.exec())
