@echo off
title Professional Invoice Manager v2.1.0

echo ================================================
echo   Professional Invoice Manager v2.1.0
echo   Starting application...
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo.
    echo 💡 Please install Python 3.7+ from https://python.org
    echo    Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Show Python version
echo 🐍 Python version:
python --version

REM Check if required packages are installed
echo.
echo 🔍 Checking dependencies...
python -c "import PyQt5; print('✅ PyQt5 found')" 2>nul
if errorlevel 1 (
    echo ❌ PyQt5 not found
    echo 🔧 Installing PyQt5...
    python -m pip install PyQt5
    if errorlevel 1 (
        echo ❌ Failed to install PyQt5
        echo 💡 Try running as administrator or install manually:
        echo    python -m pip install PyQt5
        echo.
        pause
        exit /b 1
    )
)

REM Launch the application
echo.
echo 🚀 Launching Professional Invoice Manager...
echo.
python launch_app.py

REM Check exit code
if errorlevel 1 (
    echo.
    echo ❌ Application exited with error
    echo 💡 Check the error messages above
) else (
    echo.
    echo ✅ Application closed normally
)

echo.
echo 👋 Thank you for using Professional Invoice Manager!
pause
