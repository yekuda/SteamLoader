from PySide6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QListWidget, QAbstractItemView, QPushButton, QTextEdit, QFrame, QProgressDialog, QApplication
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

class UpdateDownloaderThread(QThread):
    """Güncellemeyi arka planda indiren thread"""
    progress_updated = Signal(int)
    download_finished = Signal(str)
    download_failed = Signal(str)
    
    def __init__(self, download_url):
        super().__init__()
        self.download_url = download_url
    
    def run(self):
        from utils.utils import download_update
        try:
            file_path = download_update(
                self.download_url,
                progress_callback=lambda p: self.progress_updated.emit(p)
            )
            self.download_finished.emit(file_path)
        except Exception as e:
            self.download_failed.emit(str(e))

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
    from ui.style import (
        UPDATE_DIALOG_TITLE_STYLE, UPDATE_DIALOG_DESC_STYLE,
        UPDATE_DIALOG_NOTES_LABEL_STYLE, UPDATE_DIALOG_NOTES_TEXT_STYLE,
        UPDATE_DIALOG_DOWNLOAD_BUTTON_STYLE, UPDATE_DIALOG_CANCEL_BUTTON_STYLE
    )
    title_label = QLabel(f'Yeni Versiyon Mevcut: v{update_info["version"]}')
    title_label.setStyleSheet(UPDATE_DIALOG_TITLE_STYLE)
    layout.addWidget(title_label)
    
    # Açıklama
    desc_label = QLabel('Yeni bir güncelleme mevcut. İndirmek için aşağıdaki butona tıklayın.')
    desc_label.setStyleSheet(UPDATE_DIALOG_DESC_STYLE)
    desc_label.setWordWrap(True)
    layout.addWidget(desc_label)
    
    # Release notes (varsa)
    if update_info.get('release_notes'):
        notes_label = QLabel('Güncelleme Notları:')
        notes_label.setStyleSheet(UPDATE_DIALOG_NOTES_LABEL_STYLE)
        layout.addWidget(notes_label)
        
        notes_text = QTextEdit()
        notes_text.setReadOnly(True)
        notes_text.setMaximumHeight(150)
        notes_text.setStyleSheet(UPDATE_DIALOG_NOTES_TEXT_STYLE)
        notes_text.setPlainText(update_info['release_notes'])
        layout.addWidget(notes_text)
    
    # Butonlar
    button_layout = QVBoxLayout()
    
    download_btn = QPushButton('İndir ve Otomatik Güncelle')
    download_btn.setStyleSheet(UPDATE_DIALOG_DOWNLOAD_BUTTON_STYLE)
    
    def download_and_install_update():
        download_url = update_info.get('download_url')
        if not download_url:
            return
        
        # Progress dialog oluştur
        progress = QProgressDialog('Güncelleme indiriliyor...', 'İptal', 0, 100, parent)
        progress.setWindowTitle('Güncelleme İndiriliyor')
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        
        # İndirme thread'ini başlat
        downloader = UpdateDownloaderThread(download_url)
        downloader.setParent(parent)
        
        def update_progress(value):
            progress.setValue(value)
        
        def on_download_finished(file_path):
            progress.setValue(100)
            progress.close()
            
            # Başarı mesajı
            reply = QMessageBox.information(
                parent,
                'Güncelleme Hazır',
                'Güncelleme indirildi!\n\nUygulama kapatılacak ve yeni sürüm başlatılacak.',
                QMessageBox.Ok
            )
            
            # Yeni sürümü başlat ve uygulamayı kapat
            from utils.utils import start_new_version_and_exit
            if start_new_version_and_exit(file_path):
                dialog.accept()
                QApplication.quit()
            else:
                show_error(parent, 'Hata', 'Yeni sürüm başlatılamadı. Lütfen manuel olarak başlatın:\n' + file_path)
        
        def on_download_failed(error_msg):
            progress.close()
            show_error(parent, 'İndirme Hatası', error_msg)
        
        def on_cancelled():
            if downloader.isRunning():
                downloader.terminate()
                downloader.wait()
        
        downloader.progress_updated.connect(update_progress)
        downloader.download_finished.connect(on_download_finished)
        downloader.download_failed.connect(on_download_failed)
        progress.canceled.connect(on_cancelled)
        
        downloader.start()
        dialog.accept()
    
    download_btn.clicked.connect(download_and_install_update)
    button_layout.addWidget(download_btn)
    
    cancel_btn = QPushButton('Daha Sonra')
    cancel_btn.setStyleSheet(UPDATE_DIALOG_CANCEL_BUTTON_STYLE)
    cancel_btn.clicked.connect(dialog.reject)
    button_layout.addWidget(cancel_btn)
    
    layout.addLayout(button_layout)
    dialog.setLayout(layout)
    
    dialog.exec()