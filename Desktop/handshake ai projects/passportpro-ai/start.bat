@echo off
cd /d "%~dp0"
title PassportPro AI Server
echo ============================================
echo  PassportPro AI - Startup
echo ============================================
echo.

:: Detect Python executable
set PYTHON=
if exist "venv\Scripts\python.exe" (
    set "PYTHON=venv\Scripts\python.exe"
    echo Using virtual environment: venv\Scripts\python.exe
) else if exist "c:\Users\linga\AppData\Local\Programs\Python\Python312\python.exe" (
    set "PYTHON=c:\Users\linga\AppData\Local\Programs\Python\Python312\python.exe"
    echo Using Python 3.12: %PYTHON%
) else (
    set "PYTHON=python"
    echo Using system python
)

echo.
echo Checking environment...
%PYTHON% diagnose.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Installing required packages...
    %PYTHON% -m pip install -r requirements.txt
)

echo.
echo ============================================
echo  Starting PassportPro AI on http://127.0.0.1:5000
echo  Press Ctrl+C to stop the server.
echo ============================================
echo.

%PYTHON% run.py
pause
