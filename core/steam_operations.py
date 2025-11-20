import os
import zipfile
import shutil
import requests

def validate_app_id(app_id):
    """AppID'nin geçerli olup olmadığını Steam API'den kontrol eder"""
    try:
        api_url = f'https://store.steampowered.com/api/appdetails?appids={app_id}'
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data or not data.get(app_id):
            return False, None, "AppID Steam'de bulunamadı"
        
        app_data = data[app_id]
        if not app_data.get('success'):
            return False, None, "AppID geçersiz veya erişilemiyor"
        
        game_data = app_data.get('data', {})
        game_name = game_data.get('name', f'AppID: {app_id}')
        
        # Oyun tipini kontrol et (sadece oyunlar, DLC değil)
        game_type = game_data.get('type', '').lower()
        if game_type == 'dlc':
            return False, game_name, "Bu bir DLC, ana oyun AppID'si gerekli"
        
        return True, game_name, None
    except requests.RequestException as e:
        return False, None, f"Steam API'ye bağlanılamadı: {str(e)}"
    except Exception as e:
        return False, None, f"Doğrulama hatası: {str(e)}"

def process_zip_file(zip_path, steam_path):
    """ZIP dosyasını işler ve gerekli dosyaları Steam klasörüne kopyalar"""
    stplugin_dir = os.path.join(steam_path, 'config', 'stplug-in')
    depotcache_dir = os.path.join(steam_path, 'config', 'depotcache')
    os.makedirs(stplugin_dir, exist_ok=True)
    os.makedirs(depotcache_dir, exist_ok=True)
    
    game_id = os.path.splitext(os.path.basename(zip_path))[0]
    if not game_id.isdigit():
        raise ValueError('ZIP dosyasının adı bir AppID (sadece sayılardan oluşmalı) olmalı!')

    # AppID doğrulama (yükleme öncesi kontrol)
    is_valid, game_name, error_msg = validate_app_id(game_id)
    if not is_valid:
        error_detail = f"❌ AppID Doğrulama Başarısız\n\n{error_msg}"
        if game_name:
            error_detail += f"\n\nBulunan: {game_name}\n\nLütfen geçerli bir oyun AppID'si kullandığınızdan emin olun."
        raise ValueError(error_detail)

    # DLC bilgilerini al
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

    # ZIP dosyasındaki dosyaları çıkar
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
    
    # yekuda.lua dosyasına DLC'leri ekle
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
    
    return new_count

def delete_game_files(steam_path, game_id):
    """Belirtilen oyunun dosyalarını siler"""
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
    except Exception:
        pass  # DLC bilgisi alınamadı, sadece ana ID girdileri silinecek

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
    
    return lua_deleted, lines_removed_count

def clear_all_added_files(steam_path):
    """Tüm eklenen oyun dosyalarını temizler"""
    stplugin_dir = os.path.join(steam_path, 'config', 'stplug-in')
    depotcache_dir = os.path.join(steam_path, 'config', 'depotcache')
    
    files_deleted = 0
    
    if os.path.exists(stplugin_dir):
        for file in os.listdir(stplugin_dir):
            if file.endswith('.lua'):
                os.remove(os.path.join(stplugin_dir, file))
                files_deleted += 1

    if os.path.exists(depotcache_dir):
        for file in os.listdir(depotcache_dir):
            if file.endswith('.manifest'):
                os.remove(os.path.join(depotcache_dir, file))
                files_deleted += 1
    
    return files_deleted

def get_installed_games(steam_path):
    """Eklenen oyunları döndürür (AppID ve isim)"""
    stplugin_dir = os.path.join(steam_path, 'config', 'stplug-in')
    games = []
    
    if not os.path.exists(stplugin_dir):
        return games
    
    # stplug-in klasöründeki .lua dosyalarını bul (yekuda.lua hariç)
    for file in os.listdir(stplugin_dir):
        if file.endswith('.lua') and file != 'yekuda.lua':
            game_id = file.replace('.lua', '')
            if game_id.isdigit():
                # Steam API'den oyun ismini çek
                game_name = get_game_name_from_api(game_id)
                games.append({'id': game_id, 'name': game_name})
    
    # ID'ye göre sırala
    games.sort(key=lambda x: int(x['id']))
    return games

def get_game_name_from_api(game_id):
    """Steam API'den oyun ismini çeker"""
    try:
        api_url = f'https://store.steampowered.com/api/appdetails?appids={game_id}'
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data and data.get(game_id, {}).get('success'):
            return data[game_id].get('data', {}).get('name', f'AppID: {game_id}')
    except Exception:
        pass
    return f'AppID: {game_id}'