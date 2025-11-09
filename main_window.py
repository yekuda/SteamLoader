from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFileDialog, QApplication
)
from PySide6.QtCore import Qt

# PySide6 sabitlerini doğrudan içe aktar
AlignTop = Qt.AlignTop

import os
import sys
import zipfile

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
    handle_clear_all_files, handle_steam_restart
)
from utils.utils import download_dll_if_missing, restart_steam, load_steam_path
from core.steam_operations import process_zip_file, delete_game_files, clear_all_added_files
from ui.dialogs import show_info, show_error, confirm_action

class SteamUploader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SteamLoader')
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
        self.browse_btn.clicked.connect(lambda: handle_steam_folder_selection(self))
        self.delete_btn.clicked.connect(self.delete_game)
        self.restart_btn.clicked.connect(self.restart_steam)
        self.clear_btn.clicked.connect(self.clear_all_added_files)
    
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
        steam_path = validate_steam_path(self)
        if not steam_path:
            return
        
        try:
            new_count = process_zip_file(zip_path, steam_path)
            show_info(self, 'Başarılı', f'Oyun dosyaları başarıyla aktarıldı!\n{new_count} adet yeni DLC eklendi.')

            # --- DLL otomatik indirme ---
            download_dll_if_missing(steam_path)
            # --- Bitiş ---
        except ValueError as e:
            show_error(self, 'Hata', str(e))
        except zipfile.BadZipFile:
            show_error(self, 'Hata', 'Seçilen dosya bozuk veya geçerli bir ZIP arşivi değil.')
        except Exception as e:
            show_error(self, 'Hata', f'Bir hata oluştu:\n{e}')

    def delete_game(self):
        """Oyunu siler"""
        result, steam_path, game_id = handle_game_deletion(self)
        if not result:
            return

        try:
            lua_deleted, lines_removed_count = delete_game_files(steam_path, game_id)
            
            # Sonuç mesajını göster
            message_parts = []
            if lua_deleted:
                message_parts.append(f"• {game_id} İdli oyun silindi ve yapılandırma dosyası kaldırıldı.")
            if lines_removed_count > 0:
                message_parts.append(f"• 'yekuda.lua' dosyasından {lines_removed_count} girdi kaldırıldı.")
            
            if not message_parts:
                final_message = f"{game_id} ID'li oyuna ait herhangi bir yapılandırma dosyası veya girdisi bulunamadı."
            else:
                final_message = f"{game_id} ID'li oyun için temizleme işlemi tamamlandı:\n\n" + "\n".join(message_parts)

            show_info(self, 'İşlem Tamamlandı', final_message)
            self.delete_id_edit.clear()

        except Exception as e:
            show_error(self, 'Hata', f'Oyun silinirken bir hata oluştu:\n{e}')

    def clear_all_added_files(self):
        """Tüm eklenen dosyaları temizler"""
        steam_path = handle_clear_all_files(self)
        if not steam_path:
            return
            
        try:
            files_deleted = clear_all_added_files(steam_path)
            show_info(self, 'Başarılı', f'Tüm eklenen oyun dosyaları ve DLC girdileri temizlendi. Toplam {files_deleted} dosya silindi.')
        except Exception as e:
            show_error(self, 'Hata', f'Temizleme sırasında hata oluştu:\n{e}')

    def restart_steam(self):
        """Steam'i yeniden başlatır"""
        steam_path = handle_steam_restart(self)
        if not steam_path:
            return
            
        try:
            restart_steam(steam_path)
            show_info(self, 'Başarılı', 'Steam yeniden başlatılıyor...')
        except FileNotFoundError as e:
            show_error(self, 'Hata', str(e))
        except Exception as e:
            show_error(self, 'Hata', f'Steam yeniden başlatılamadı:\n{e}')