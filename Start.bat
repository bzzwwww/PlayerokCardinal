@echo off
setlocal
cd /d %~dp0
title Playerok Cardinal

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found.
    echo Run Setup.bat first.
    pause
    exit /b 1
)

call .venv\Scripts\python.exe main.py
pause
