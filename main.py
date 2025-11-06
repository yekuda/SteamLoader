import sys
import os
import subprocess
import zipfile
import shutil
import requests
import json
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, 
    QFileDialog, QMessageBox, QHBoxLayout, QFrame, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont, QDesktopServices, QIcon

# --- STYLESHEETS ---

# Ana stil (font-family ve butonlar için font-weight eklendi)
DARK_PURPLE_STYLE = '''
QWidget {
    background: #252622;  /* Darker than #373934 */
    color: #d0d0d0;       /* Slightly darker than #f0f0f0 */
    font-family: 'Segoe UI'; /* Tüm uygulama için modern bir font */
}
QLabel {
    color: #d0d0d0;
}
QLineEdit {
    border: 2px solid #9c783e;  /* Darker, more muted version of #C3974E */
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
    background: #1d1e1a;        /* Darker background */
    color: #d0d0d0;
}
QPushButton {
    background: #9c783e;        /* Darker, more muted version of #C3974E */
    color: #f0f0f0;
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 14px;
    font-weight: bold; /* Buton metinlerini daha belirgin yapar */
}
QPushButton:hover {
    background: #8a6a35;        /* Even darker for hover effect */
}
/* YENİ: Silme butonu için farklı bir stil */
QPushButton#deleteButton {
    background-color: #992e22; /* Darker red */
}
QPushButton#deleteButton:hover {
    background-color: #80261d; /* Darker red for hover */
}
QMessageBox {
    background-color: #1d1e1a;
}
QMessageBox QLabel {
    color: #d0d0d0;
    font-size: 14px;
}
QMessageBox QPushButton {
    background: #9c783e;
    color: #f0f0f0;
    border-radius: 8px;
    padding: 6px 18px;
    font-size: 13px;
    font-weight: bold; /* Mesaj kutusu butonları da belirgin olsun */
}
QMessageBox QPushButton:hover {
    background: #8a6a35;
}
'''

# DragDropLabel için stil (kod tekrarını önlemek için tek bir değişkende toplandı)
DRAG_DROP_STYLE = '''
QLabel {
    border: 3px dashed #9c783e;
    border-radius: 16px;
    background: #1d1e1a;
    color: #9c783e;
    font-size: 18px;
    font-weight: bold; /* Metni daha dikkat çekici yapar */
    padding: 40px;
    margin-top: 10px;
    margin-bottom: 10px;
}
QLabel:hover {
    background: #353632;
    color: #d0d0d0;
}
'''

# --- WIDGETS ---

class DragDropLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText('Oyun dosyasını buraya sürükleyin veya seçin')
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(DRAG_DROP_STYLE)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self.setStyleSheet(DRAG_DROP_STYLE + 'QLabel { background: #353632; }')
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet(DRAG_DROP_STYLE)

    def dropEvent(self, event):
        self.setStyleSheet(DRAG_DROP_STYLE)
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().endswith('.zip'):
                    self.parent().process_zip(url.toLocalFile())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent().select_zip_file()

class SteamUploader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SteamLoader')
        self.setMinimumSize(580, 560) # YENİ: Yükseklik artırıldı
        self.setStyleSheet(DARK_PURPLE_STYLE)
        self.setWindowIcon(QIcon("favicon.ico"))  # icon.ico exe ile aynı klasörde olmalı
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15) # Spacing ayarlandı

        title = QLabel('SteamLoader')
        title.setFont(QFont('Segoe UI', 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('color: #9c783e; margin-bottom: 0px;')  # Darker, more muted version of #C3974E
        main_layout.addWidget(title)

        desc = QLabel('Steam yolunu seçin ve oyunun ZIP dosyasını sürükleyip bırakın.\nDosyalar otomatik olarak Steam klasörünüze aktarılacaktır.')
        desc.setFont(QFont('Segoe UI', 12))
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet('color: #b0b0b0; margin-bottom: 10px;')  # More muted color
        desc.setWordWrap(True)
        main_layout.addWidget(desc)

        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText('Steam klasörünü seçin...')
        path_layout.addWidget(self.path_edit, stretch=3)
        self.browse_btn = QPushButton('Gözat')
        path_layout.addWidget(self.browse_btn, stretch=1)
        self.browse_btn.clicked.connect(self.select_steam_folder)
        main_layout.addLayout(path_layout)

        self.dragdrop_label = DragDropLabel(self)
        main_layout.addWidget(self.dragdrop_label, stretch=1)
        
        # --- YENİ: Oyunu Silme Bölümü ---
        delete_layout = QHBoxLayout()
        self.delete_id_edit = QLineEdit()
        self.delete_id_edit.setPlaceholderText("Silinecek Oyun ID'sini Girin...")
        delete_layout.addWidget(self.delete_id_edit, stretch=3)

        self.delete_btn = QPushButton("Oyunu Sil")
        self.delete_btn.setObjectName("deleteButton") # Stil için ID ataması
        self.delete_btn.clicked.connect(self.delete_game)
        delete_layout.addWidget(self.delete_btn, stretch=1)
        
        main_layout.addLayout(delete_layout)
        # --- Bitiş: Oyunu Silme Bölümü ---
        
        # Ayırıcı
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #9c783e;")  # Darker, more muted version of #C3974E
        main_layout.addWidget(line)

        self.restart_btn = QPushButton("Steam'i Yeniden Başlat")
        main_layout.addWidget(self.restart_btn)
        self.restart_btn.clicked.connect(self.restart_steam)

        self.clear_btn = QPushButton("Tüm Eklenen Oyunları Temizle")
        main_layout.addWidget(self.clear_btn)
        self.clear_btn.clicked.connect(self.clear_all_added_files)

        main_layout.addStretch(1)
        self.setLayout(main_layout)

    # --- YENİ: Oyunu Silme Fonksiyonu ---
    def delete_game(self):
        steam_path = self.path_edit.text().strip()
        game_id_str = self.delete_id_edit.text().strip()

        if not steam_path or not os.path.isdir(steam_path):
            self.show_info('Hata', 'Lütfen geçerli bir Steam klasörü seçin!')
            return
        if not game_id_str.isdigit():
            self.show_info('Hata', "Lütfen geçerli bir Oyun ID'si girin!")
            return
        
        game_id = game_id_str
        reply = QMessageBox.question(self, 'Onay', f"{game_id} ID'li oyun ve ilgili tüm DLC girdileri yapılandırmadan kaldırılacak.\n\nBu işlem geri alınamaz. Emin misiniz?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        try:
            stplugin_dir = os.path.join(steam_path, 'config', 'stplug-in')
            
            # 1. Oyuna özel .lua dosyasını sil
            game_lua_path = os.path.join(stplugin_dir, f'{game_id}.lua')
            lua_deleted = False
            if os.path.exists(game_lua_path):
                os.remove(game_lua_path)
                lua_deleted = True

            # 2. Ana oyun ID'si ve DLC ID'lerini topla
            all_ids_to_remove = {game_id}
            try:
                api_url = f'https://store.steampowered.com/api/appdetails?appids={game_id}'
                response = requests.get(api_url, timeout=10)
                response.raise_for_status()
                data = response.json()
                if data and data.get(game_id, {}).get('success'):
                    dlc_ids = data[game_id].get('data', {}).get('dlc', [])
                    if isinstance(dlc_ids, list):
                        for dlc in dlc_ids:
                            all_ids_to_remove.add(str(dlc))
            except Exception as e:
                print(f"DLC bilgisi alınamadı, sadece ana ID ({game_id}) girdileri silinecek: {e}")

            # 3. yekuda.lua dosyasını temizle
            yekuda_path = os.path.join(stplugin_dir, 'yekuda.lua')
            lines_kept = []
            lines_removed_count = 0
            if os.path.exists(yekuda_path):
                with open(yekuda_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        is_line_to_remove = False
                        for id_to_remove in all_ids_to_remove:
                            if f'addappid({id_to_remove},' in line.replace(" ", ""):
                                is_line_to_remove = True
                                break
                        if not is_line_to_remove:
                            lines_kept.append(line)
                        else:
                            lines_removed_count += 1
                
                with open(yekuda_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines_kept)
            
            # 4. Sonuç mesajını göster
            message_parts = []
            if lua_deleted:
                message_parts.append(f"• {game_id} İdli oyun silindi ve yapılandırma dosyası kaldırıldı.")
            if lines_removed_count > 0:
                message_parts.append(f"• 'yekuda.lua' dosyasından {lines_removed_count} girdi kaldırıldı.")
            
            if not message_parts:
                final_message = f"{game_id} ID'li oyuna ait herhangi bir yapılandırma dosyası veya girdisi bulunamadı."
            else:
                final_message = f"{game_id} ID'li oyun için temizleme işlemi tamamlandı:\n\n" + "\n".join(message_parts)

            self.show_info('İşlem Tamamlandı', final_message)
            self.delete_id_edit.clear()

        except Exception as e:
            self.show_info('Hata', f'Oyun silinirken bir hata oluştu:\n{e}')

    def clear_all_added_files(self):
        steam_path = self.path_edit.text().strip()
        if not steam_path:
            self.show_info('Hata', 'Lütfen önce Steam klasörünü seçin!')
            return
        reply = QMessageBox.question(
            self,
            'Onay',
            "Tüm eklenen oyun dosyaları ve DLC girdileri kalıcı olarak silinecek. Emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No        
        )
        if reply == QMessageBox.Yes:
            try:
                stplugin_dir = os.path.join(steam_path, 'config', 'stplug-in')
                depotcache_dir = os.path.join(steam_path, 'config', 'depotcache')
                
                if os.path.exists(stplugin_dir):
                    for file in os.listdir(stplugin_dir):
                        if file.endswith('.lua'):
                            os.remove(os.path.join(stplugin_dir, file))

                if os.path.exists(depotcache_dir):
                    for file in os.listdir(depotcache_dir):
                        if file.endswith('.manifest'):
                            os.remove(os.path.join(depotcache_dir, file))

                self.show_info('Başarılı', 'Tüm eklenen oyun dosyaları ve DLC girdileri temizlendi.')
            except Exception as e:
                self.show_info('Hata', f'Temizleme sırasında hata oluştu:\n{e}')

    def select_steam_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Steam klasörünü seçin')
        if folder:
            self.path_edit.setText(folder)

    def select_zip_file(self):
        file, _ = QFileDialog.getOpenFileName(self, 'ZIP dosyası seçin', '', 'ZIP Dosyası (*.zip)')
        if file:
            self.process_zip(file)

    def show_info(self, title, message):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Information)
        msg.exec()

    def process_zip(self, zip_path):
        steam_path = self.path_edit.text().strip()
        if not steam_path or not os.path.isdir(steam_path):
            self.show_info('Hata', 'Lütfen geçerli bir Steam klasörü seçin!')
            return
        
        stplugin_dir = os.path.join(steam_path, 'config', 'stplug-in')
        depotcache_dir = os.path.join(steam_path, 'config', 'depotcache')
        os.makedirs(stplugin_dir, exist_ok=True)
        os.makedirs(depotcache_dir, exist_ok=True)
        
        try:
            game_id = os.path.splitext(os.path.basename(zip_path))[0]
            if not game_id.isdigit():
                self.show_info('Hata', 'ZIP dosyasının adı bir AppID (sadece sayılardan oluşmalı) olmalı!')
                return

            api_url = f'https://store.steampowered.com/api/appdetails?appids={game_id}'
            dlc_ids = []
            try:
                response = requests.get(api_url, timeout=10)
                response.raise_for_status()
                data = response.json()
                if data and data.get(game_id, {}).get('success'):
                    dlc_ids = data[game_id].get('data', {}).get('dlc', [])
                    if not isinstance(dlc_ids, list):
                        dlc_ids = []
            except requests.RequestException:
                pass 

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    if file_info.is_dir():
                        continue
                    
                    target_dir = None
                    if file_info.filename.endswith('.lua'):
                        target_dir = stplugin_dir
                    elif file_info.filename.endswith('.manifest'):
                        target_dir = depotcache_dir
                    
                    if target_dir:
                        target_path = os.path.join(target_dir, os.path.basename(file_info.filename))
                        with zip_ref.open(file_info) as source, open(target_path, 'wb') as target:
                            shutil.copyfileobj(source, target)
            
            yekuda_path = os.path.join(stplugin_dir, 'yekuda.lua')
            existing_lines = set()
            if os.path.exists(yekuda_path):
                with open(yekuda_path, 'r', encoding='utf-8') as f:
                    existing_lines = {line.strip() for line in f}

            new_count = 0
            with open(yekuda_path, 'a', encoding='utf-8') as f:
                for dlc_id in dlc_ids:
                    add_line = f'addappid({dlc_id}, 1)'
                    if add_line not in existing_lines:
                        f.write(add_line + '\n')
                        new_count += 1
            
            self.show_info('Başarılı', f'Oyun dosyaları başarıyla aktarıldı!\n{new_count} adet yeni DLC eklendi.')

            # --- DLL otomatik indirme ---
            try:
                dll_url = "http://yekuda.com/dll/hid.dll"  # kendi bağlantın
                dll_target = os.path.join(steam_path, "hid.dll")

                if not os.path.exists(dll_target):
                    response = requests.get(dll_url, timeout=15)
                    response.raise_for_status()
                    with open(dll_target, "wb") as f:
                        f.write(response.content)
                    print(f"hid.dll indirildi ve {dll_target} konumuna kaydedildi.")
                else:
                    print("hid.dll zaten mevcut, indirme atlandı.")
            except Exception as e:
                print(f".dll indirilemedi: {e}")
            # --- Bitiş ---

        except zipfile.BadZipFile:
            self.show_info('Hata', 'Seçilen dosya bozuk veya geçerli bir ZIP arşivi değil.')
        except Exception as e:
            self.show_info('Hata', f'Bir hata oluştu:\n{e}')



    def restart_steam(self):
        steam_path = self.path_edit.text().strip()
        if not steam_path:
            self.show_info('Hata', 'Lütfen önce Steam klasörünü seçin!')
            return
        
        steam_exe = os.path.join(steam_path, 'steam.exe')
        if not os.path.exists(steam_exe):
            self.show_info('Hata', 'steam.exe bulunamadı! Lütfen doğru Steam klasörünü seçtiğinizden emin olun.')
            return
            
        try:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/F', '/IM', 'steam.exe'], check=True, shell=True)
                subprocess.Popen([steam_exe])
            else:
                subprocess.run(['killall', '-9', 'steam'], check=True)
                subprocess.Popen([steam_exe])
            
            self.show_info('Başarılı', 'Steam yeniden başlatılıyor...')
        except (subprocess.CalledProcessError, FileNotFoundError):
             self.show_info('Hata', 'Steam kapatılamadı. Lütfen manuel olarak kapatıp tekrar deneyin.')
        except Exception as e:
            self.show_info('Hata', f'Steam yeniden başlatılamadı:\n{e}')

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