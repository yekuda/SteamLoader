import os
import subprocess
import requests
import json
import shutil
import re
import tempfile
import sys

# Uygulama versiyonu
APP_VERSION = "1.1.3"

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

def download_update(download_url, progress_callback=None):
    """Güncellemeyi indirir ve dosya yolunu döndürür"""
    try:
        # Temp klasöründe indirme yap
        temp_dir = tempfile.gettempdir()
        filename = os.path.basename(download_url)
        if not filename.endswith('.exe'):
            filename = 'SteamLoader_Update.exe'
        
        file_path = os.path.join(temp_dir, filename)
        
        # Dosyayı indir
        response = requests.get(download_url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    
                    # Progress callback
                    if progress_callback and total_size > 0:
                        progress = int((downloaded_size / total_size) * 100)
                        progress_callback(progress)
        
        return file_path
    except Exception as e:
        raise Exception(f'İndirme hatası: {str(e)}')

def start_new_version_and_exit(new_exe_path):
    """Yeni sürümü başlatır ve mevcut uygulamayı kapatır"""
    try:
        # Mevcut exe'nin yolunu al
        if getattr(sys, 'frozen', False):
            # PyInstaller ile derlenmiş exe
            current_exe = sys.executable
        else:
            # Python script olarak çalışıyor (development)
            current_exe = os.path.abspath(sys.argv[0])
        
        if sys.platform == 'win32':
            # Batch script oluştur
            batch_script = os.path.join(tempfile.gettempdir(), 'update_steamloader.bat')
            
            with open(batch_script, 'w', encoding='ansi') as f:  # ANSI encoding kullan
                f.write('@echo off\n')
                f.write('title SteamLoader Guncelleniyor\n')
                f.write('echo SteamLoader guncelleniyor, lutfen bekleyin...\n')
                f.write('timeout /t 3 /nobreak > nul\n')  # 3 saniye bekle
                f.write(f'del /f /q "{current_exe}" 2>nul\n')  # Eski exe'yi sil
                f.write(f'move /y "{new_exe_path}" "{current_exe}"\n')  # Yeni exe'yi yerine koy
                f.write('if exist "{current_exe}" (\n')
                f.write(f'  start "" "{current_exe}"\n')  # Yeni exe'yi başlat
                f.write(') else (\n')
                f.write('  echo HATA: Dosya kopyalanamadi!\n')
                f.write('  pause\n')
                f.write(')\n')
                f.write(f'del /f /q "{batch_script}" 2>nul\n')  # Script'i kendini sil
            
            # Batch script'i görünür pencerede çalıştır (debug için)
            subprocess.Popen(['cmd', '/c', batch_script])
        else:
            # Linux/Mac için basit yöntem
            shutil.move(new_exe_path, current_exe)
            os.chmod(current_exe, 0o755)
            subprocess.Popen([current_exe])
        
        return True
    except Exception as e:
        return False