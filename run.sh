#!/bin/bash

# Set the Python interpreter and virtual environment directory to use
# On Linux/macOS, it is generally recommended to use python3
PYTHON="python3"
VENV_DIR="./venv"

# Check if Python is installed
if ! command -v $PYTHON &> /dev/null
then
    echo "$PYTHON is not installed or not found in PATH."
    read -p "Press Enter to exit..."
    exit 1
fi

# Check and create virtual environment
# On Linux/macOS, the activation script is located at venv/bin/activate
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "Creating virtual environment..."
    $PYTHON -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        read -p "Press Enter to exit..."
        exit 1
    fi

    echo "Activating virtual environment and installing/updating dependencies..."
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"

    echo "Upgrading pip..."
    $PYTHON -m pip install --upgrade pip

    echo "Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Failed to install dependencies."
        read -p "Press Enter to exit..."
        exit 1
    fi
else
    # If the virtual environment already exists, activate it directly
    source "$VENV_DIR/bin/activate"
fi

echo "Starting the application..."
# Run the main program, note that the path separator is /
$PYTHON app/aquarius/main.py
