@echo off
setlocal

echo ================================================
echo   Generando TraductorEnVivo.exe
echo ================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] No se encontro Python en el PATH.
    echo Instalalo desde https://www.python.org/downloads/
    echo (importante: tildar "Add Python to PATH" durante la instalacion)
    pause
    exit /b 1
)

echo Creando entorno virtual de compilacion...
python -m venv venv_build
call venv_build\Scripts\activate.bat

echo.
echo Instalando dependencias...
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

echo.
echo Compilando el ejecutable (esto puede tardar 1-2 minutos)...
pyinstaller --onefile --windowed --name TraductorEnVivo main.py

echo.
echo ================================================
echo   Listo.
echo   El ejecutable quedo en: dist\TraductorEnVivo.exe
echo ================================================
echo.
echo Si vas a instalarlo en varias PCs, seguí con installer.iss
echo (necesita Inno Setup, ver README.md).
echo.
pause
