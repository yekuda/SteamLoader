from PySide6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QListWidget, QAbstractItemView, QPushButton, QTextEdit, QFrame
from PySide6.QtCore import Qt, QThread, Signal, QUrl
from PySide6.QtGui import QDesktopServices, QFont

# PySide6 sabitlerini doğrudan içe aktar
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

class GamesLoaderThread(QThread):
    """Oyunları arka planda yükleyen thread"""
    games_loaded = Signal(list)
    
    def __init__(self, steam_path):
        super().__init__()
        self.steam_path = steam_path
    
    def run(self):
        from core.steam_operations import get_installed_games
        try:
            games = get_installed_games(self.steam_path)
            self.games_loaded.emit(games)
        except Exception:
            self.games_loaded.emit([])

def show_games_dialog(parent, steam_path):
    """Eklenen oyunları gösteren dialog penceresi"""
    from ui.style import (
        MAIN_WINDOW_STYLE, GAMES_DIALOG_TITLE_STYLE, 
        GAMES_DIALOG_SUBTITLE_STYLE, GAMES_DIALOG_SEPARATOR_STYLE,
        GAMES_DIALOG_LIST_STYLE
    )
    
    dialog = QDialog(parent)
    dialog.setWindowTitle('Eklenen Oyunlar')
    dialog.setMinimumSize(600, 500)
    dialog.setStyleSheet(MAIN_WINDOW_STYLE)
    
    layout = QVBoxLayout()
    layout.setContentsMargins(25, 25, 25, 25)
    layout.setSpacing(20)
    
    # Başlık container
    title_container = QVBoxLayout()
    title_container.setSpacing(8)
    
    # Ana başlık
    title_label = QLabel('Eklenen Oyunlar')
    title_label.setStyleSheet(GAMES_DIALOG_TITLE_STYLE)
    title_container.addWidget(title_label)
    
    # Alt başlık (oyun sayısı için)
    subtitle_label = QLabel('Oyunlar yükleniyor...')
    subtitle_label.setStyleSheet(GAMES_DIALOG_SUBTITLE_STYLE)
    title_container.addWidget(subtitle_label)
    
    # Alt çizgi
    separator = QFrame()
    separator.setFrameShape(QFrame.HLine)
    separator.setFrameShadow(QFrame.Sunken)
    separator.setStyleSheet(GAMES_DIALOG_SEPARATOR_STYLE)
    title_container.addWidget(separator)
    
    layout.addLayout(title_container)
    
    # Liste widget
    list_widget = QListWidget()
    # Bold font ayarla
    bold_font = QFont()
    bold_font.setBold(True)
    bold_font.setPointSize(14)
    list_widget.setFont(bold_font)
    list_widget.setStyleSheet(GAMES_DIALOG_LIST_STYLE)
    list_widget.setSelectionMode(QAbstractItemView.NoSelection)
    list_widget.setFocusPolicy(Qt.NoFocus)
    
    # Yükleniyor mesajı
    list_widget.addItem('⏳ Oyunlar yükleniyor...')
    
    layout.addWidget(list_widget, stretch=1)
    dialog.setLayout(layout)
    
    # Thread oluştur ve başlat
    loader_thread = GamesLoaderThread(steam_path)
    loader_thread.setParent(dialog)  # Thread'i dialog'a bağla
    
    def update_games_list(games_list):
        if dialog.isVisible():  # Dialog hala açıksa güncelle
            list_widget.clear()
            if not games_list:
                list_widget.addItem('Henüz oyun eklenmemiş')
                subtitle_label.setText('Toplam 0 oyun')
            else:
                game_count = len(games_list)
                subtitle_label.setText(f'Toplam {game_count} oyun')
                for game in games_list:
                    # Oyun adı ve ID'yi daha güzel göster
                    game_text = f"{game['name']}\n   ID: {game['id']}"
                    list_widget.addItem(game_text)
    
    loader_thread.games_loaded.connect(update_games_list)
    loader_thread.finished.connect(loader_thread.deleteLater)  # Thread bitince temizle
    loader_thread.start()
    
    dialog.exec()
    
    # Dialog kapatıldığında thread'in bitmesini bekle
    # Thread'in hala var olup olmadığını kontrol et
    try:
        if loader_thread.isRunning():
            loader_thread.terminate()
            loader_thread.wait(1000)  # En fazla 1 saniye bekle
    except RuntimeError:
        # Thread zaten silinmiş, bir şey yapma
        pass