@echo off
chcp 65001 >nul
echo.
echo ╔════════════════════════════════════════╗
echo ║   SteamLoader Builder                 ║
echo ║   EXE Oluştur                         ║
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

echo ╔════════════════════════════════════════╗
echo ║   ✓ BUILD BAŞARILI!                   ║
echo ╚════════════════════════════════════════╝
echo.
echo 📦 Çıktı dosyası:
echo   • EXE: dist\SteamLoader.exe
echo.

echo.
pause
