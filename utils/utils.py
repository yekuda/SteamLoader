import os
import subprocess
import requests

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