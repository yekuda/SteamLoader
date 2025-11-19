from PySide6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QListWidget, QAbstractItemView
from PySide6.QtCore import Qt, QThread, Signal

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
    from ui.style import LIST_WIDGET_STYLE, MAIN_WINDOW_STYLE
    
    dialog = QDialog(parent)
    dialog.setWindowTitle('Eklenen Oyunlar')
    dialog.setMinimumSize(500, 400)
    dialog.setStyleSheet(MAIN_WINDOW_STYLE)
    
    layout = QVBoxLayout()
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(15)
    
    # Başlık
    title_label = QLabel('Eklenen Oyunlar')
    title_label.setStyleSheet('''
        color: #9c783e;
        font-weight: bold;
        font-size: 18px;
        padding: 0px;
        margin: 0px;
    ''')
    layout.addWidget(title_label)
    
    # Liste widget
    list_widget = QListWidget()
    list_widget.setStyleSheet(LIST_WIDGET_STYLE)
    list_widget.setSelectionMode(QAbstractItemView.NoSelection)
    list_widget.setFocusPolicy(Qt.NoFocus)
    
    # Yükleniyor mesajı
    list_widget.addItem('Oyunlar yükleniyor...')
    
    layout.addWidget(list_widget)
    dialog.setLayout(layout)
    
    # Thread oluştur ve başlat
    loader_thread = GamesLoaderThread(steam_path)
    loader_thread.setParent(dialog)  # Thread'i dialog'a bağla
    
    def update_games_list(games_list):
        if dialog.isVisible():  # Dialog hala açıksa güncelle
            list_widget.clear()
            if not games_list:
                list_widget.addItem('Henüz oyun eklenmemiş')
            else:
                for game in games_list:
                    list_widget.addItem(f"{game['name']} (ID: {game['id']})")
    
    loader_thread.games_loaded.connect(update_games_list)
    loader_thread.finished.connect(loader_thread.deleteLater)  # Thread bitince temizle
    loader_thread.start()
    
    dialog.exec()
    
    # Dialog kapatıldığında thread'in bitmesini bekle
    if loader_thread.isRunning():
        loader_thread.terminate()
        loader_thread.wait(1000)  # En fazla 1 saniye bekle