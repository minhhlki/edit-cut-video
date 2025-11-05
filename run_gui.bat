@echo off
REM Video Cutter GUI Launcher for Windows
REM Double-click this file to launch the GUI application

echo.
echo ========================================
echo   Video Cutter Tool - GUI Launcher
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo Starting Video Cutter GUI...
echo.

REM Run the GUI application
python video_cutter_gui.py

REM If there's an error, pause so user can see the message
if errorlevel 1 (
    echo.
    echo An error occurred!
    pause
)
