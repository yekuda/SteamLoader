import os
from ui.dialogs import show_info, show_error, confirm_action
from utils.utils import save_steam_path

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