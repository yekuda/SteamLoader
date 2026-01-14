"""
SteamLoader - Merkezi Sürüm Yönetimi
=====================================
Bu dosya uygulamanın sürüm bilgisini tek noktadan yönetir.
Hem Python kodu hem de build sistemi bu dosyayı kullanır.

Sürüm Numarası: MAJOR.MINOR.PATCH
- MAJOR: Büyük değişiklikler, geriye uyumsuzluklar
- MINOR: Yeni özellikler, geriye uyumlu
- PATCH: Hata düzeltmeleri, küçük iyileştirmeler
"""

# Sürüm bilgileri
__version__ = "1.0.0"
__app_name__ = "SteamLoader"
__author__ = "Yekuda"
__description__ = "Steam Workshop İçerik Yükleyici"
__url__ = "https://github.com/yekuda/SteamLoader"

# Detaylı sürüm bilgileri
VERSION_INFO = {
    "version": __version__,
    "app_name": __app_name__,
    "author": __author__,
    "description": __description__,
    "url": __url__,
}

def get_version():
    """Sadece sürüm numarasını döndürür"""
    return __version__

def get_full_version():
    """Tam sürüm bilgisini döndürür"""
    return f"{__app_name__} v{__version__}"

def get_version_info():
    """Tüm sürüm bilgilerini döndürür"""
    return VERSION_INFO

if __name__ == "__main__":
    # Test amaçlı
    print(f"{__app_name__} v{__version__}")
    print(f"Yazar: {__author__}")
    print(f"Açıklama: {__description__}")
