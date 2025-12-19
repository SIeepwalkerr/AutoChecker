@echo off
chcp 65001 >nul
title VK Auto Read
color 0A

echo ╔════════════════════════════════════════╗
echo ║   VK Auto Read - Launcher              ║
echo ╚════════════════════════════════════════╝
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python не найден!
    echo Скачайте: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Выберите:
echo 1. GUI приложение
echo 2. Простой скрипт
echo 3. Установить зависимости
echo.

set /p choice="Выбор: "

if "%choice%"=="1" (
    python vk_auto_read_gui.py
)
if "%choice%"=="2" (
    python vk_auto_read.py
)
if "%choice%"=="3" (
    pip install -r requirements.txt
    pause
)

pause