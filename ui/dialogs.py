from PySide6.QtWidgets import QMessageBox

# PySide6 sabitlerini doğrudan içe aktar
from PySide6.QtWidgets import QMessageBox
Information = QMessageBox.Information
Critical = QMessageBox.Critical
Yes = QMessageBox.Yes
No = QMessageBox.No

def show_info(parent, title, message):
    """Bilgi mesajı kutusu gösterir"""
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setIcon(Information)
    msg.exec()

def show_error(parent, title, message):
    """Hata mesajı kutusu gösterir"""
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setIcon(Critical)
    msg.exec()

def confirm_action(parent, title, message):
    """Onay isteyen mesaj kutusu gösterir"""
    reply = QMessageBox.question(
        parent,
        title,
        message,
        Yes | No,
        No
    )
    return reply == Yes