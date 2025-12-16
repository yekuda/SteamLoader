@echo off
chcp 65001 >nul
echo.
echo ╔════════════════════════════════════════╗
echo ║   SteamLoader Installer Builder       ║
echo ║   Profesyonel Kurulum Paketi Oluştur  ║
echo ╚════════════════════════════════════════╝
echo.

:: Mevcut versiyonu göster (Python ile güvenli şekilde al)
for /f "delims=" %%a in ('python -c "import version; print(version.__version__)"') do set VERSION=%%a
set STEAMLOADER_VERSION=%VERSION%
echo ► Mevcut Sürüm: %VERSION%
echo ► Sürümü değiştirmek için: version.py dosyasını düzenleyin
echo.

:: Temizlik
echo ► Önceki build dosyaları temizleniyor...
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist installer_output rd /s /q installer_output
if exist __pycache__ rd /s /q __pycache__
echo ✓ Temizlendi
echo.

:: PyInstaller ile EXE oluştur
echo ► PyInstaller ile uygulama derleniyor...
pyinstaller --name=SteamLoader --onefile --windowed --icon=favicon.ico --add-data="favicon.ico;." --clean --noconfirm main.py
if errorlevel 1 (
    echo ✗ PyInstaller hatası!
    pause
    exit /b 1
)
echo ✓ Uygulama başarıyla derlendi!
echo.

:: Inno Setup ile installer oluştur
echo ► Inno Setup ile installer oluşturuluyor...
set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC="C:\Program Files\Inno Setup 6\ISCC.exe"

if exist %ISCC% (
    %ISCC% installer.iss
    if errorlevel 1 (
        echo ✗ Inno Setup hatası!
        pause
        exit /b 1
    )
    echo ✓ Installer başarıyla oluşturuldu!
    echo.
    echo ╔════════════════════════════════════════╗
    echo ║   ✓ BUILD BAŞARILI!                   ║s
    echo ╚════════════════════════════════════════╝
    echo.
    echo 📦 Çıktı dosyaları:
    echo   • EXE: dist\SteamLoader.exe
    echo   • Installer: installer_output\SteamLoader_Setup_v%VERSION%.exe
    echo.
    echo Artık installer'ı paylaşabilirsiniz!
) else (
    echo ✗ Inno Setup bulunamadı!
    echo ⚠ EXE hazır: dist\SteamLoader.exe
    echo ⚠ Installer için Inno Setup kurun: https://jrsoftware.org/isdl.php
)

echo.
pause
