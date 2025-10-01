@echo off
set "PYTHON=python"
set "VENV_DIR=.\venv"

REM Check if Python is installed
%PYTHON% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    pause
    exit /b 1
)

REM Check and create venv environment
if not exist "%VENV_DIR%\Scripts\activate" (
    echo Creating virtual environment...
    %PYTHON% -m venv %VENV_DIR%
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
    
    echo Activating virtual environment and installing/updating dependencies...
    call %VENV_DIR%\Scripts\activate.bat
    
    echo Upgrading pip...
    %PYTHON% -m pip install --upgrade pip
    
    echo Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Failed to install dependencies.
        pause
        exit /b 1
    )
)

REM Activate venv and run the application
echo Activating virtual environment and starting the application...
call %VENV_DIR%\Scripts\activate.bat
%PYTHON% app\aquarius\main.py

pause