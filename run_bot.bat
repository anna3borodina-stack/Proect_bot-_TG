@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Запуск NEWGOLD бота...
python main.py
if errorlevel 1 pause
