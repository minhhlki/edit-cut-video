#!/bin/bash
#
# Video Cutter Tool - Auto Installation Script for Ubuntu
# Usage: curl -fsSL https://raw.githubusercontent.com/YOUR_REPO/main/install.sh | bash
#

set -e

echo "================================================"
echo "🎬 Video Cutter Tool - Auto Installer"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_green() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_yellow() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_red() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if running on Ubuntu/Debian
if ! command -v apt-get &> /dev/null; then
    print_red "This script is for Ubuntu/Debian systems only!"
    exit 1
fi

print_green "Detected Ubuntu/Debian system"
echo ""

# Update package list
echo "📦 Updating package list..."
sudo apt-get update -qq

# Install Python 3 if not installed
if ! command -v python3 &> /dev/null; then
    echo "📦 Installing Python 3..."
    sudo apt-get install -y python3 python3-pip python3-tk
    print_green "Python 3 installed"
else
    print_green "Python 3 already installed ($(python3 --version))"
fi

# Install pip if not installed
if ! command -v pip3 &> /dev/null; then
    echo "📦 Installing pip..."
    sudo apt-get install -y python3-pip
    print_green "pip installed"
else
    print_green "pip already installed"
fi

# Install ffmpeg if not installed
if ! command -v ffmpeg &> /dev/null; then
    echo "📦 Installing ffmpeg..."
    sudo apt-get install -y ffmpeg
    print_green "ffmpeg installed"
else
    print_green "ffmpeg already installed ($(ffmpeg -version | head -n1))"
fi

# Install git if not installed
if ! command -v git &> /dev/null; then
    echo "📦 Installing git..."
    sudo apt-get install -y git
    print_green "git installed"
else
    print_green "git already installed"
fi

# Install curl if not installed
if ! command -v curl &> /dev/null; then
    echo "📦 Installing curl..."
    sudo apt-get install -y curl
    print_green "curl installed"
else
    print_green "curl already installed"
fi

echo ""
echo "📥 Installing Python dependencies..."

# Install yt-dlp
if ! python3 -c "import yt_dlp" 2>/dev/null; then
    echo "Installing yt-dlp..."
    pip3 install yt-dlp --quiet
    print_green "yt-dlp installed"
else
    print_green "yt-dlp already installed"
fi

# Install Google Drive API client (optional)
if ! python3 -c "import googleapiclient" 2>/dev/null; then
    echo "Installing Google Drive API client..."
    pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib --quiet
    print_green "Google Drive API client installed"
else
    print_green "Google Drive API client already installed"
fi

echo ""
echo "📂 Setting up Video Cutter Tool..."

# Create installation directory
INSTALL_DIR="$HOME/video-cutter-tool"
if [ ! -d "$INSTALL_DIR" ]; then
    mkdir -p "$INSTALL_DIR"
    print_green "Created directory: $INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# Download all necessary files
echo "📥 Downloading tool files..."

# List of files to download
FILES=(
    "video_cutter.py"
    "youtube_downloader.py"
    "google_drive_uploader.py"
    "video_cutter_interactive.py"
    "video_cutter_gui.py"
)

# GitHub raw URL base (UPDATE THIS WITH YOUR REPO)
REPO_BASE="https://raw.githubusercontent.com/minhhlki/edit-cut-video/main"

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        print_yellow "$file already exists, skipping..."
    else
        echo "Downloading $file..."
        if curl -fsSL "$REPO_BASE/$file" -o "$file" 2>/dev/null; then
            chmod +x "$file"
            print_green "Downloaded $file"
        else
            print_yellow "Could not download $file (may not exist yet)"
        fi
    fi
done

# Create directories
mkdir -p downloads
mkdir -p temp_segments

echo ""
print_green "Installation complete!"
echo ""
echo "================================================"
echo "🚀 How to use:"
echo "================================================"
echo ""
echo "1. Interactive CLI (Recommended):"
echo "   cd $INSTALL_DIR"
echo "   python3 video_cutter_interactive.py"
echo ""
echo "2. GUI:"
echo "   cd $INSTALL_DIR"
echo "   python3 video_cutter_gui.py"
echo ""
echo "3. Command line:"
echo "   cd $INSTALL_DIR"
echo "   python3 video_cutter.py -i input.mp4 -s \"segments\" -o output.mp4"
echo ""
echo "================================================"
echo ""

# Ask if user wants to run interactive mode now
read -p "Do you want to run interactive mode now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "video_cutter_interactive.py" ]; then
        python3 video_cutter_interactive.py
    else
        print_yellow "Interactive script not found. Creating it now..."
        # Create interactive script inline
        cat > video_cutter_interactive.py << 'EOFPYTHON'
#!/usr/bin/env python3
print("Interactive mode script will be created separately")
EOFPYTHON
        print_yellow "Please run: python3 video_cutter_interactive.py"
    fi
else
    echo "You can run it later with:"
    echo "  cd $INSTALL_DIR && python3 video_cutter_interactive.py"
fi

echo ""
print_green "Setup complete! Enjoy using Video Cutter Tool! 🎬"
