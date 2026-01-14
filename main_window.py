from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFileDialog, QApplication, QLabel, QPushButton
)
from PySide6.QtCore import Qt

# PySide6 sabitlerini doğrudan içe aktar
AlignTop = Qt.AlignTop

import os
import sys

# Kendi modüllerimizi içe aktar
from ui.style import MAIN_WINDOW_STYLE
from ui.widgets import DragDropLabel
from ui.ui_components import (
    create_title_label, create_description_label, 
    create_path_selection_layout, create_delete_game_layout,
    create_separator_line, create_action_buttons
)
from core.event_handlers import (
    handle_steam_folder_selection, handle_zip_file_selection,
    validate_steam_path, handle_game_deletion, 
    handle_clear_all_files, handle_steam_restart,
    handle_zip_processing, handle_game_deletion_complete,
    handle_clear_all_complete, handle_steam_restart_complete,
    handle_show_games_list
)
from utils.utils import load_steam_path, APP_VERSION



class SteamUploader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f'SteamLoader v{APP_VERSION}')
        self.setMinimumSize(580, 560)
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        # Basit bir simge - varsayılan pencere simgesini kullan
        
        # Dosya diyaloglarını oluştur
        self.file_dialog = QFileDialog()
        
        # Arayüzü oluştur
        self.setup_ui()
        
        # Olay bağlamalarını yap
        self.setup_connections()
        
        # Kaydedilmiş Steam klasör yolunu yükle
        self.load_saved_steam_path()

    def setup_ui(self):
        """Arayüzü oluşturur"""
        main_layout = QVBoxLayout()
        main_layout.setAlignment(AlignTop)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15)

        # Başlık ve açıklama
        main_layout.addWidget(create_title_label())
        main_layout.addWidget(create_description_label())

        # Steam klasörü seçimi
        self.path_layout, self.path_edit, self.browse_btn = create_path_selection_layout(self)
        main_layout.addLayout(self.path_layout)

        # Sürükle-bırak alanı
        self.dragdrop_label = DragDropLabel(self)
        main_layout.addWidget(self.dragdrop_label, stretch=1)
        
        # Eklenen oyunlar butonu
        self.show_games_btn = QPushButton("Eklenen Oyunları Göster")
        # Stil diğer butonlarla aynı (MAIN_WINDOW_STYLE'den otomatik uygulanır)
        main_layout.addWidget(self.show_games_btn)
        
        # Oyun silme bölümü
        self.delete_layout, self.delete_id_edit, self.delete_btn = create_delete_game_layout(self)
        main_layout.addLayout(self.delete_layout)
        
        # Ayırıcı çizgi
        main_layout.addWidget(create_separator_line())

        # Eylem düğmeleri
        self.restart_btn, self.clear_btn = create_action_buttons()
        main_layout.addWidget(self.restart_btn)
        main_layout.addWidget(self.clear_btn)

        main_layout.addStretch(1)
        self.setLayout(main_layout)

    def setup_connections(self):
        """Olay bağlamalarını yapar"""
        self.browse_btn.clicked.connect(lambda: self.on_steam_path_selected())
        self.delete_btn.clicked.connect(self.delete_game)
        self.restart_btn.clicked.connect(self.restart_steam)
        self.clear_btn.clicked.connect(self.clear_all_added_files)
        self.show_games_btn.clicked.connect(self.toggle_games_list)
    
    def on_steam_path_selected(self):
        """Steam klasörü seçildiğinde çağrılır"""
        handle_steam_folder_selection(self)
    
    def load_saved_steam_path(self):
        """Kaydedilmiş Steam klasör yolunu yükler"""
        saved_path = load_steam_path()
        if saved_path and os.path.isdir(saved_path):
            self.path_edit.setText(saved_path)

    def select_zip_file(self):
        """ZIP dosyası seçimi"""
        handle_zip_file_selection(self)

    def process_zip(self, zip_path):
        """ZIP dosyasını işler"""
        handle_zip_processing(self, zip_path)

    def delete_game(self):
        """Oyunu siler"""
        result, steam_path, game_id = handle_game_deletion(self)
        if not result:
            return
        
        if handle_game_deletion_complete(self, steam_path, game_id):
            self.delete_id_edit.clear()

    def clear_all_added_files(self):
        """Tüm eklenen dosyaları temizler"""
        steam_path = handle_clear_all_files(self)
        if not steam_path:
            return
        
        handle_clear_all_complete(self, steam_path)

    def restart_steam(self):
        """Steam'i yeniden başlatır"""
        steam_path = handle_steam_restart(self)
        if not steam_path:
            return
        
        handle_steam_restart_complete(self, steam_path)
    
    def toggle_games_list(self):
        """Eklenen oyunlar listesini dialog penceresinde göster"""
        handle_show_games_list(self)
    
