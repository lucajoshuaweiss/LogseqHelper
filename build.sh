#!/bin/bash
set -e

ENV_DIR=".venv"
PYTHON=python3

command -v $PYTHON >/dev/null 2>&1 || PYTHON=python

if [ -d "$ENV_DIR" ]; then
    echo "Virtual environment already exists."
else
    echo "Creating virtual environment in ./$ENV_DIR"
    $PYTHON -m venv "$ENV_DIR"
fi

source "$ENV_DIR/bin/activate"

echo "Installing dependencies..."
python -m pip install -r requirements.txt

echo "Cleaning old builds..."
rm -rf build dist *.spec

echo "Building application..."
pyinstaller --onefile --windowed \
  --collect-all PIL \
  main.py

deactivate
echo "Done. Virtual environment deactivated."