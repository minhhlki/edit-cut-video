#!/bin/bash
# Video Cutter GUI Launcher for Linux/macOS
# Run this file to launch the GUI application: ./run_gui.sh

echo ""
echo "========================================"
echo "  Video Cutter Tool - GUI Launcher"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo ""
    echo "Please install Python 3:"
    echo "  - Ubuntu/Debian: sudo apt-get install python3"
    echo "  - macOS: brew install python3"
    echo ""
    exit 1
fi

echo "Starting Video Cutter GUI..."
echo ""

# Run the GUI application
python3 video_cutter_gui.py

# Check exit status
if [ $? -ne 0 ]; then
    echo ""
    echo "An error occurred!"
    read -p "Press Enter to exit..."
fi
