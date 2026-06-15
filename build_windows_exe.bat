@echo off
chcp 65001 >nul 2>&1
title EcoDash — Build Windows EXE
echo.
echo ============================================================
echo  EcoDash Collector — Build do executavel Windows
echo  Requer: Python 3.10+ no PATH
echo ============================================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado no PATH.
    echo Instale em https://www.python.org/downloads/
    pause & exit /b 1
)

echo [1/4] Instalando dependencias de build...
pip install pyinstaller psutil requests --quiet
if errorlevel 1 ( echo [ERRO] Falha ao instalar dependencias. & pause & exit /b 1 )

echo [2/4] Copiando collector_windows.py...
if not exist "collector_windows.py" (
    echo [ERRO] Arquivo collector_windows.py nao encontrado.
    echo Execute este .bat na pasta ecodash-server\
    pause & exit /b 1
)

echo [3/4] Gerando ecodash-collector.exe (aguarde ~1 min)...
pyinstaller ^
    --onefile ^
    --name ecodash-collector ^
    --console ^
    --hidden-import psutil ^
    --hidden-import requests ^
    --distpath dist_windows ^
    --workpath build_tmp ^
    --specpath build_tmp ^
    collector_windows.py
if errorlevel 1 ( echo [ERRO] Falha no PyInstaller. & pause & exit /b 1 )

echo [4/4] Copiando para static/...
if not exist "static" mkdir static
copy /Y "dist_windows\ecodash-collector.exe" "static\ecodash-collector.exe"

echo.
echo ============================================================
echo  Build concluido!
echo  Arquivo: static\ecodash-collector.exe
echo  Tamanho:
for %%F in (static\ecodash-collector.exe) do echo    %%~zF bytes
echo.
echo  Proximos passos:
echo  1. Suba o servidor Django (python manage.py runserver)
echo  2. No frontend: EcoDash > Analise > Download EXE
echo  3. Baixe tambem o ecodash.conf personalizado
echo  4. Coloque os dois na mesma pasta e execute:
echo       ecodash-collector.exe python seu_app.py
echo ============================================================
echo.
pause
