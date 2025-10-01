#!/bin/bash

# 切换到脚本所在目录
cd "$(dirname "$0")"

VENV_DIR="./venv"

echo "Activating virtual environment..."
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "Virtual environment not found. Please run run.sh first."
    exit 1
fi
source "$VENV_DIR/bin/activate"

echo "Updating yt-dlp..."
pip install --upgrade yt-dlp

echo "Updating requirements.txt..."
pip freeze > requirements.txt

echo "yt-dlp has been updated successfully."