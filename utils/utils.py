import os
import subprocess
import requests
import json
import shutil
import re

# Uygulama versiyonu
APP_VERSION = "1.0.0"

def download_dll_if_missing(steam_path):
    """DLL dosyasını indirir (eksikse)"""
    try:
        dll_url = "http://yekuda.com/dll/hid.dll"  # kendi bağlantın
        dll_target = os.path.join(steam_path, "hid.dll")

        if not os.path.exists(dll_target):
            response = requests.get(dll_url, timeout=15)
            response.raise_for_status()
            with open(dll_target, "wb") as f:
                f.write(response.content)
            print(f"hid.dll indirildi ve {dll_target} konumuna kaydedildi.")
            return True
        else:
            print("hid.dll zaten mevcut, indirme atlandı.")
            return False
    except Exception as e:
        print(f".dll indirilemedi: {e}")
        return False

def restart_steam(steam_path):
    """Steam'i yeniden başlatır"""
    steam_exe = os.path.join(steam_path, 'steam.exe')
    if not os.path.exists(steam_exe):
        raise FileNotFoundError('steam.exe bulunamadı! Lütfen doğru Steam klasörünü seçtiğinizden emin olun.')
        
    try:
        if os.name == 'nt':
            subprocess.run(['taskkill', '/F', '/IM', 'steam.exe'], check=True, shell=True)
            subprocess.Popen([steam_exe])
        else:
            subprocess.run(['killall', '-9', 'steam'], check=True)
            subprocess.Popen([steam_exe])
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise Exception('Steam kapatılamadı. Lütfen manuel olarak kapatıp tekrar deneyin.')
    except Exception as e:
        raise Exception(f'Steam yeniden başlatılamadı: {e}')

def get_config_path():
    """Config dosyasının yolunu döndürür (AppData/Local/SteamLoader)"""
    if os.name == 'nt':  # Windows
        appdata = os.getenv('LOCALAPPDATA')
        if not appdata:
            appdata = os.path.join(os.getenv('USERPROFILE', ''), 'AppData', 'Local')
        config_dir = os.path.join(appdata, 'SteamLoader')
    else:  # Linux/Mac
        config_dir = os.path.join(os.path.expanduser('~'), '.config', 'SteamLoader')
    
    # Klasör yoksa oluştur
    os.makedirs(config_dir, exist_ok=True)
    
    config_path = os.path.join(config_dir, 'config.json')
    
    # Eski konumdaki config dosyasını yeni konuma taşı (bir kez)
    old_config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    if os.path.exists(old_config_path) and not os.path.exists(config_path):
        try:
            shutil.move(old_config_path, config_path)
        except Exception:
            pass  # Taşıma başarısız olursa devam et
    
    return config_path

def save_steam_path(steam_path):
    """Steam klasör yolunu config dosyasına kaydeder"""
    try:
        config_path = get_config_path()
        config = {}
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except (json.JSONDecodeError, IOError):
                config = {}
        
        config['steam_path'] = steam_path
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Config kaydedilemedi: {e}")
        return False

def load_steam_path():
    """Config dosyasından Steam klasör yolunu yükler"""
    try:
        config_path = get_config_path()
        if not os.path.exists(config_path):
            return None
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('steam_path', None)
    except (json.JSONDecodeError, IOError, KeyError):
        return None

def check_for_updates(current_version):
    """GitHub Releases API'den güncelleme kontrolü yapar"""
    try:
        api_url = "https://api.github.com/repos/yekuda/SteamLoader/releases/latest"
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        latest_version = data.get('tag_name', '').lstrip('v')
        download_url = None
        
        # Asset'lerden .exe dosyasını bul
        for asset in data.get('assets', []):
            if asset.get('name', '').endswith('.exe'):
                download_url = asset.get('browser_download_url')
                break
        
        # Versiyon karşılaştırması
        if compare_versions(latest_version, current_version) > 0:
            return {
                'available': True,
                'version': latest_version,
                'download_url': download_url,
                'release_notes': data.get('body', '')
            }
        
        return {'available': False}
    except Exception as e:
        print(f"Güncelleme kontrolü başarısız: {e}")
        return {'available': False, 'error': str(e)}

def compare_versions(v1, v2):
    """İki versiyon numarasını karşılaştırır (1: v1 > v2, 0: eşit, -1: v1 < v2)"""
    def normalize_version(v):
        # Versiyon numarasını normalize et (örn: "1.0.0" -> [1, 0, 0])
        parts = re.findall(r'\d+', v)
        return [int(x) for x in parts]
    
    v1_parts = normalize_version(v1)
    v2_parts = normalize_version(v2)
    
    # Eksik kısımları 0 ile doldur
    max_len = max(len(v1_parts), len(v2_parts))
    v1_parts.extend([0] * (max_len - len(v1_parts)))
    v2_parts.extend([0] * (max_len - len(v2_parts)))
    
    for i in range(max_len):
        if v1_parts[i] > v2_parts[i]:
            return 1
        elif v1_parts[i] < v2_parts[i]:
            return -1
    
    return 0