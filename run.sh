#!/bin/bash

# 切换到脚本所在目录
cd "$(dirname "$0")"

PYTHON="python3"
VENV_DIR="./venv"

# 检查 Python 是否安装
if ! command -v $PYTHON &> /dev/null
then
    echo "Python3 is not installed or not in PATH."
    exit 1
fi

# 检查并创建 venv 环境
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    $PYTHON -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        exit 1
    fi

    echo "Installing dependencies..."
    source $VENV_DIR/bin/activate
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Failed to install dependencies."
        exit 1
    fi
    deactivate
fi

# 激活 venv 并运行程序
echo "Activating virtual environment and starting the application..."
source $VENV_DIR/bin/activate
$PYTHON app/aquarius/main.py
