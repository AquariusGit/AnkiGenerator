@echo off
set "PYTHON=python"
set "VENV_DIR=.\venv"

REM 检查 Python 是否安装
%PYTHON% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    pause
    exit /b 1
)

REM 检查并创建 venv 环境
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

REM 会报 使用pydub库 报ModuleNotFoundError: No module named 'audioop'

REM 激活 venv 并运行程序
echo Activating virtual environment and starting the application...
call %VENV_DIR%\Scripts\activate.bat
%PYTHON% app\aquarius\main.py

pause
