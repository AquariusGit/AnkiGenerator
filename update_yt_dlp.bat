@echo off
setlocal

set "PYTHON=python"
set "VENV_DIR=.\venv"

echo Activating virtual environment...
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Virtual environment not found. Please run run.bat first.
    pause
    exit /b 1
)
call "%VENV_DIR%\Scripts\activate.bat"

echo Updating yt-dlp...
pip install --upgrade yt-dlp

echo Updating requirements.txt...
pip freeze > requirements.txt

echo.
echo yt-dlp has been updated successfully.
pause