@echo off
setlocal
cd /d %~dp0
title PlayerokCardinal Setup

echo ========================================
echo  PlayerokCardinal - Setup
echo ========================================
echo.

call :resolve_python
if not defined PYTHON_CMD (
    echo.
    echo ERROR: Python 3 not found!
    echo Install Python 3.11+ from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [1/4] Using Python: %PYTHON_CMD%
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [2/4] Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [2/4] Virtual environment already exists.
)
echo.

echo [3/4] Upgrading pip, setuptools and wheel...
call .venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo.
    echo ERROR: Failed to upgrade pip tools.
    pause
    exit /b 1
)
echo.

echo [4/4] Installing dependencies from requirements.txt...
call .venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)
echo.

echo ========================================
echo  Setup completed successfully!
echo ========================================
echo.
echo Now run Start.bat
echo.
pause
exit /b 0

:resolve_python
py -3.11 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py -3.11"
    goto :eof
)
py -3 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
    goto :eof
)
python --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python"
    goto :eof
)
goto :eof
