import os
import zipfile
from ui.dialogs import show_info, show_error, confirm_action
from utils.utils import save_steam_path, download_dll_if_missing
from core.steam_operations import process_zip_file, delete_game_files, clear_all_added_files, validate_app_id

def handle_steam_folder_selection(parent):
    """Steam klasörü seçimini işler"""
    folder = parent.file_dialog.getExistingDirectory(parent, 'Steam klasörünü seçin')
    if folder:
        parent.path_edit.setText(folder)
        # Seçilen klasörü config dosyasına kaydet
        save_steam_path(folder)

def handle_zip_file_selection(parent):
    """ZIP dosyası seçimini işler"""
    file, _ = parent.file_dialog.getOpenFileName(parent, 'ZIP dosyası seçin', '', 'ZIP Dosyası (*.zip)')
    if file:
        parent.process_zip(file)

def validate_steam_path(parent):
    """Steam yolunu doğrular"""
    steam_path = parent.path_edit.text().strip()
    if not steam_path or not os.path.isdir(steam_path):
        show_info(parent, 'Hata', 'Lütfen geçerli bir Steam klasörü seçin!')
        return None
    return steam_path

def handle_game_deletion(parent):
    """Oyun silme işlemini işler"""
    steam_path = validate_steam_path(parent)
    if not steam_path:
        return False, None, None
        
    game_id_str = parent.delete_id_edit.text().strip()
    if not game_id_str.isdigit():
        show_info(parent, 'Hata', "Lütfen geçerli bir Oyun ID'si girin!")
        return False, None, None
    
    game_id = game_id_str
    message = f"{game_id} ID'li oyun ve ilgili tüm DLC girdileri yapılandırmadan kaldırılacak.\n\nBu işlem geri alınamaz. Emin misiniz?"
    result = confirm_action(parent, 'Onay', message)
    return result, steam_path, game_id

def handle_clear_all_files(parent):
    """Tüm eklenen dosyaları temizleme işlemini işler"""
    steam_path = validate_steam_path(parent)
    if not steam_path:
        return None
        
    message = "Tüm eklenen oyun dosyaları ve DLC girdileri kalıcı olarak silinecek. Emin misiniz?"
    if not confirm_action(parent, 'Onay', message):
        return None
        
    return steam_path

def handle_steam_restart(parent):
    """Steam yeniden başlatma işlemini işler"""
    steam_path = validate_steam_path(parent)
    if not steam_path:
        return None
    return steam_path

def handle_zip_processing(parent, zip_path):
    """ZIP dosyası işleme mantığını yönetir"""
    steam_path = validate_steam_path(parent)
    if not steam_path:
        return
    
    try:
        # AppID doğrulama ve oyun adını al
        game_id = os.path.splitext(os.path.basename(zip_path))[0]
        game_name = None
        if game_id.isdigit():
            is_valid, game_name, _ = validate_app_id(game_id)
        
        new_count = process_zip_file(zip_path, steam_path)
        
        # Başarılı mesajında oyun adını göster
        if game_name:
            show_info(parent, 'Başarılı', f'{game_name}\n\nOyun dosyaları başarıyla aktarıldı!\n{new_count} adet yeni DLC eklendi.')
        else:
            show_info(parent, 'Başarılı', f'Oyun dosyaları başarıyla aktarıldı!\n{new_count} adet yeni DLC eklendi.')

        # DLL otomatik indirme
        download_dll_if_missing(steam_path)
        
    except ValueError as e:
        show_error(parent, 'Hata', str(e))
    except zipfile.BadZipFile:
        show_error(parent, 'Hata', 'Seçilen dosya bozuk veya geçerli bir ZIP arşivi değil.')
    except Exception as e:
        show_error(parent, 'Hata', f'Bir hata oluştu:\n{e}')

def handle_game_deletion_complete(parent, steam_path, game_id):
    """Oyun silme işlemini tamamlar ve sonucu gösterir"""
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

        show_info(parent, 'İşlem Tamamlandı', final_message)
        return True
    except Exception as e:
        show_error(parent, 'Hata', f'Oyun silinirken bir hata oluştu:\n{e}')
        return False

def handle_clear_all_complete(parent, steam_path):
    """Tüm dosyaları temizleme işlemini tamamlar"""
    try:
        files_deleted = clear_all_added_files(steam_path)
        show_info(parent, 'Başarılı', f'Tüm eklenen oyun dosyaları ve DLC girdileri temizlendi. Toplam {files_deleted} dosya silindi.')
    except Exception as e:
        show_error(parent, 'Hata', f'Temizleme sırasında hata oluştu:\n{e}')

def handle_steam_restart_complete(parent, steam_path):
    """Steam yeniden başlatma işlemini tamamlar"""
    from utils.utils import restart_steam
    try:
        restart_steam(steam_path)
        show_info(parent, 'Başarılı', 'Steam yeniden başlatılıyor...')
    except FileNotFoundError as e:
        show_error(parent, 'Hata', str(e))
    except Exception as e:
        show_error(parent, 'Hata', f'Steam yeniden başlatılamadı:\n{e}')

def handle_show_games_list(parent):
    """Eklenen oyunlar listesini gösterir"""
    from ui.dialogs import show_games_dialog
    steam_path = parent.path_edit.text().strip()
    if not steam_path or not os.path.isdir(steam_path):
        show_info(parent, 'Bilgi', 'Lütfen önce geçerli bir Steam klasörü seçin!')
        return
    
    show_games_dialog(parent, steam_path)