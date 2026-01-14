import os
import subprocess
import requests
import json
import shutil

# Merkezi version.py dosyasından sürüm bilgisini al
from version import __version__ as APP_VERSION

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
            return True
        else:
            return False
    except Exception:
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