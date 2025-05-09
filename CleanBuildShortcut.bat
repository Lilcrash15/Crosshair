@echo off
echo Cleaning old build files...
rmdir /s /q build
rmdir /s /q dist
del /q crosshair_overlay.spec

echo Building new .exe...
py -3.10 -m PyInstaller crosshair_overlay.py ^
  --noconsole --onefile --windowed ^
  --add-data "icon.ico;." ^
  --add-data "icon-hidden.ico;." ^
  --add-data "Biting My Nails.otf;." ^
  --clean

echo Creating desktop shortcut...

powershell -NoProfile -ExecutionPolicy Bypass -File "%cd%\create_shortcut.ps1"

echo Done! Shortcut created on your desktop.
pause