@echo off
setlocal

set ENV_DIR=.venv
set PYTHON=python

where %PYTHON% >nul 2>nul
if errorlevel 1 (
    echo Python not found. Please install Python and add it to PATH.
    exit /b 1
)

IF EXIST "%ENV_DIR%" (
    echo Virtual environment already exists.
) ELSE (
    echo Creating virtual environment in .\%ENV_DIR%
    %PYTHON% -m venv "%ENV_DIR%"
    if errorlevel 1 (
        echo Failed to create virtual environment.
        exit /b 1
    )
)

call "%ENV_DIR%\Scripts\activate.bat"

echo Installing dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

echo Cleaning old builds...
IF EXIST build rmdir /s /q build
IF EXIST dist rmdir /s /q dist
del /q *.spec 2>nul

echo Building application...
pyinstaller --onefile --windowed ^
  --collect-all PIL ^
  main.py

if errorlevel 1 exit /b 1

call deactivate

echo Done. Virtual environment deactivated.
endlocal