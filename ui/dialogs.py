from PySide6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QListWidget, QAbstractItemView, QPushButton, QTextEdit
from PySide6.QtCore import Qt, QThread, Signal, QUrl
from PySide6.QtGui import QDesktopServices

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

def show_update_dialog(parent, update_info):
    """Güncelleme mevcut olduğunda gösterilen dialog"""
    from ui.style import MAIN_WINDOW_STYLE
    
    dialog = QDialog(parent)
    dialog.setWindowTitle('Güncelleme Mevcut')
    dialog.setMinimumSize(500, 400)
    dialog.setStyleSheet(MAIN_WINDOW_STYLE)
    
    layout = QVBoxLayout()
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(15)
    
    # Başlık
    title_label = QLabel(f'Yeni Versiyon Mevcut: v{update_info["version"]}')
    title_label.setStyleSheet('''
        color: #9c783e;
        font-weight: bold;
        font-size: 18px;
        padding: 0px;
        margin: 0px;
    ''')
    layout.addWidget(title_label)
    
    # Açıklama
    desc_label = QLabel('Yeni bir güncelleme mevcut. İndirmek için aşağıdaki butona tıklayın.')
    desc_label.setStyleSheet('color: #d0d0d0; font-size: 13px;')
    desc_label.setWordWrap(True)
    layout.addWidget(desc_label)
    
    # Release notes (varsa)
    if update_info.get('release_notes'):
        notes_label = QLabel('Güncelleme Notları:')
        notes_label.setStyleSheet('color: #9c783e; font-weight: bold; font-size: 14px; margin-top: 10px;')
        layout.addWidget(notes_label)
        
        notes_text = QTextEdit()
        notes_text.setReadOnly(True)
        notes_text.setMaximumHeight(150)
        notes_text.setStyleSheet('''
            QTextEdit {
                border: 2px solid #9c783e;
                border-radius: 8px;
                background: #1d1e1a;
                color: #d0d0d0;
                font-size: 12px;
                padding: 5px;
            }
        ''')
        notes_text.setPlainText(update_info['release_notes'])
        layout.addWidget(notes_text)
    
    # Butonlar
    button_layout = QVBoxLayout()
    
    download_btn = QPushButton('İndir ve Aç')
    download_btn.setStyleSheet('''
        QPushButton {
            background: #9c783e;
            color: #f0f0f0;
            border-radius: 8px;
            padding: 10px;
            font-size: 14px;
            font-weight: bold;
        }
        QPushButton:hover {
            background: #8a6a35;
        }
    ''')
    
    def download_update():
        if update_info.get('download_url'):
            QDesktopServices.openUrl(QUrl(update_info['download_url']))
        dialog.accept()
    
    download_btn.clicked.connect(download_update)
    button_layout.addWidget(download_btn)
    
    cancel_btn = QPushButton('Daha Sonra')
    cancel_btn.setStyleSheet('''
        QPushButton {
            background: #353632;
            color: #d0d0d0;
            border: 2px solid #9c783e;
            border-radius: 8px;
            padding: 8px;
            font-size: 13px;
        }
        QPushButton:hover {
            background: #9c783e;
            color: #f0f0f0;
        }
    ''')
    cancel_btn.clicked.connect(dialog.reject)
    button_layout.addWidget(cancel_btn)
    
    layout.addLayout(button_layout)
    dialog.setLayout(layout)
    
    dialog.exec()