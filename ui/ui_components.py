from PySide6.QtWidgets import (
    QLabel, QPushButton, QLineEdit, QFrame, QHBoxLayout, QVBoxLayout, QListWidget, QWidget, QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# PySide6 sabitlerini doğrudan içe aktar
AlignCenter = Qt.AlignCenter
Bold = QFont.Bold
HLine = QFrame.HLine
Sunken = QFrame.Sunken
NoFocus = Qt.NoFocus

def create_title_label():
    """Başlık etiketini oluşturur"""
    title = QLabel('SteamLoader')
    title.setFont(QFont('Segoe UI', 24, Bold))
    title.setAlignment(AlignCenter)
    title.setStyleSheet('color: #9c783e; margin-bottom: 0px;')
    return title

def create_description_label():
    """Açıklama etiketini oluşturur"""
    desc = QLabel('Steam yolunu seçin ve oyunun ZIP dosyasını sürükleyip bırakın.\nDosyalar otomatik olarak Steam klasörünüze aktarılacaktır.')
    desc.setFont(QFont('Segoe UI', 12))
    desc.setAlignment(AlignCenter)
    desc.setStyleSheet('color: #b0b0b0; margin-bottom: 10px;')
    desc.setWordWrap(True)
    return desc

def create_path_selection_layout(parent):
    """Yol seçimi arayüzünü oluşturur"""
    path_layout = QHBoxLayout()
    path_edit = QLineEdit()
    path_edit.setPlaceholderText('Steam klasörünü seçin...')
    path_edit.setReadOnly(True)  # Kullanıcı manuel yazı yazamaz, sadece Gözat ile seçebilir
    browse_btn = QPushButton('Gözat')
    path_layout.addWidget(path_edit, stretch=3)
    path_layout.addWidget(browse_btn, stretch=1)
    return path_layout, path_edit, browse_btn

def create_delete_game_layout(parent):
    """Oyun silme arayüzünü oluşturur"""
    delete_layout = QHBoxLayout()
    delete_id_edit = QLineEdit()
    delete_id_edit.setPlaceholderText("Silinecek Oyun ID'sini Girin...")
    delete_btn = QPushButton("Oyunu Sil")
    delete_btn.setObjectName("deleteButton")
    delete_layout.addWidget(delete_id_edit, stretch=3)
    delete_layout.addWidget(delete_btn, stretch=1)
    return delete_layout, delete_id_edit, delete_btn

def create_separator_line():
    """Ayırıcı çizgiyi oluşturur"""
    line = QFrame()
    line.setFrameShape(HLine)
    line.setFrameShadow(Sunken)
    line.setStyleSheet("background-color: #9c783e;")
    return line

def create_action_buttons():
    """Eylem düğmelerini oluşturur"""
    restart_btn = QPushButton("Steam'i Yeniden Başlat")
    clear_btn = QPushButton("Tüm Eklenen Oyunları Temizle")
    return restart_btn, clear_btn

def create_games_list_widget():
    """Eklenen oyunlar listesi widget'ını oluşturur"""
    from ui.style import LIST_WIDGET_STYLE, GAMES_CONTAINER_STYLE
    
    # Container widget oluştur
    container = QWidget()
    container.setStyleSheet(GAMES_CONTAINER_STYLE)
    
    # Layout oluştur
    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    
    # Başlık
    title_label = QLabel('Eklenen Oyunlar')
    title_label.setStyleSheet('''
        color: #9c783e;
        font-weight: bold;
        font-size: 14px;
        padding: 0px;
        margin: 0px;
    ''')
    layout.addWidget(title_label)
    
    # Liste widget
    games_list = QListWidget()
    games_list.setStyleSheet(LIST_WIDGET_STYLE)
    games_list.setMaximumHeight(140)
    games_list.setMinimumHeight(80)
    games_list.setSelectionMode(QAbstractItemView.NoSelection)  # Seçimi devre dışı bırak
    games_list.setFocusPolicy(Qt.NoFocus)  # Focus'u devre dışı bırak
    layout.addWidget(games_list)
    
    container.setLayout(layout)
    return container, games_list