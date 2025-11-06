# 🚀 Quick Start Guide

## One-Line Installation (Ubuntu/Debian)

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/edit-cut-video/main/install.sh -o install.sh && chmod +x install.sh && ./install.sh
```

**⚠️ Note**: Replace `YOUR_USERNAME` with your actual GitHub username.

## What the installer does:

1. ✅ Checks and installs Python 3
2. ✅ Checks and installs ffmpeg
3. ✅ Installs yt-dlp (for YouTube downloads)
4. ✅ Installs Google Drive API (for auto-upload)
5. ✅ Downloads all tool files
6. ✅ Sets up directory structure
7. ✅ Offers to run interactive mode immediately

## After Installation

The tool will be installed in: `~/video-cutter-tool/`

### Run Interactive Mode (Recommended):

```bash
cd ~/video-cutter-tool
python3 video_cutter_interactive.py
```

You'll be prompted for:
- YouTube URL (optional)
- Input video path
- Segments to cut
- Output video path
- Processing mode (1=Fast, 2=Balanced, 3=Accurate)
- Audio on/off
- Google Drive upload (optional with JSON key)

### Run GUI:

```bash
cd ~/video-cutter-tool
python3 video_cutter_gui.py
```

### Run CLI:

```bash
cd ~/video-cutter-tool
python3 video_cutter.py -i input.mp4 -s "segments" -o output.mp4
```

## Example Interactive Session:

```
================================================
🎬 VIDEO CUTTER TOOL - Interactive Mode
================================================

------------------------------------------------------------
STEP 1: Video Source
------------------------------------------------------------
🔗 YouTube URL (Optional, press Enter to skip): https://youtube.com/watch?v=...

📥 Downloading video from YouTube...
------------------------------------------------------------
✅ Downloaded successfully: downloads/video.mp4

------------------------------------------------------------
STEP 2: Segments to Cut
------------------------------------------------------------
Format: MM:SS-MM:SS|MM:SS-MM:SS|...
Example: 03:05-03:10|40:05-40:10|1:03:05-1:04:05

✂️  Segments: 00:30-01:00|05:00-05:30|10:00-10:30

✅ Valid format! Found 3 segments:
  Segment 1: 30s - 60s (30s)
  Segment 2: 300s - 330s (30s)
  Segment 3: 600s - 630s (30s)

Total output duration: 90s (1.50 minutes)

------------------------------------------------------------
STEP 3: Output Configuration
------------------------------------------------------------
💾 Output video path [video_cut.mp4]: highlights.mp4

⚙️  Processing mode
  1. 🚀 Fast - Rất nhanh (10-20x, có thể sai lệch ±1-2s)
  2. ⚡ Balanced - Cân bằng (3-4x, chính xác 100%) (default)
  3. 🎯 Accurate - Chính xác tuyệt đối (chậm nhất)

Your choice [1-3]: 2

🔊 Remove audio (create silent video)? [y/N]: n

------------------------------------------------------------
STEP 4: Google Drive Upload (Optional)
------------------------------------------------------------
📤 Upload to Google Drive after processing? [y/N]: y

📤 Google Drive Upload Configuration
------------------------------------------------------------
Please paste your Google Drive service account JSON key.
(Paste the entire JSON content, then press Enter twice)

Paste JSON (press Enter twice when done):
{paste your JSON here}

✅ Valid Google Drive credentials!

------------------------------------------------------------
📋 SUMMARY
------------------------------------------------------------
Input: downloads/video.mp4
Segments: 3 segments
Output: highlights.mp4
Mode: BALANCED
Audio: ON
Google Drive Upload: YES
------------------------------------------------------------

▶️  Start processing? [Y/n]: y

============================================================
🎬 PROCESSING VIDEO
============================================================

⚡ BALANCED MODE (Nhanh + Chính xác)
🔊 Âm thanh: Bật (Giữ nguyên)

🔄 Đang cắt 3 đoạn song song với 3 luồng...

✅ [1/3] Đoạn 1: 00:30.000 → 01:00.000 (Độ dài: 00:30.000)
✅ [2/3] Đoạn 2: 05:00.000 → 05:30.000 (Độ dài: 00:30.000)
✅ [3/3] Đoạn 3: 10:00.000 → 10:30.000 (Độ dài: 00:30.000)

✅ Đã cắt xong 3 đoạn
⚡ Thời gian cắt: 25.3s

🔗 Đang ghép các đoạn lại với nhau...
✨ Hoàn thành! Video đã được lưu tại: highlights.mp4
📊 Thống kê:
   - Thời gian cắt: 25.3s
   - Thời gian ghép: 1.2s
   - Tổng thời gian: 26.5s
   - Tốc độ xử lý: 3.4x realtime

============================================================
✅ VIDEO PROCESSING COMPLETE!
============================================================

📁 Output saved to: highlights.mp4

📤 Uploading to Google Drive...
------------------------------------------------------------
📁 Found existing folder: Video Cutter Uploads
📤 Uploading: highlights.mp4
████████████████████████████████ 100.0% | 15.3/15.3 MB
✅ Upload complete!
📄 File ID: 1abc...xyz
🔗 Link: https://drive.google.com/file/d/...

✅ Upload to Google Drive complete!

🎉 All done! Thank you for using Video Cutter Tool!
```

## Google Drive Setup

To enable automatic upload to Google Drive:

1. **Create a Google Cloud Project**
   - Go to: https://console.cloud.google.com/
   - Create a new project

2. **Enable Google Drive API**
   - In your project, go to "APIs & Services"
   - Click "Enable APIs and Services"
   - Search for "Google Drive API"
   - Click "Enable"

3. **Create Service Account**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in details and create
   - Click on the created service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create New Key"
   - Choose "JSON"
   - Download the JSON file

4. **Share Drive Folder (Optional)**
   - Open Google Drive
   - Create a folder for uploads
   - Right-click > "Share"
   - Add the service account email (from JSON: `client_email`)
   - Give "Editor" permission

5. **Use in Interactive Mode**
   - When prompted, paste the entire JSON content
   - Press Enter twice when done
   - Videos will automatically upload after processing

## Troubleshooting

### ffmpeg not found
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

### yt-dlp not found
```bash
pip3 install yt-dlp
```

### Google Drive API not found
```bash
pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### Permission denied on install.sh
```bash
chmod +x install.sh
./install.sh
```

## Manual Installation

If the one-liner doesn't work:

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-tk ffmpeg git curl

# Install Python packages
pip3 install yt-dlp google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Clone repository
git clone https://github.com/YOUR_USERNAME/edit-cut-video.git
cd edit-cut-video

# Run interactive mode
python3 video_cutter_interactive.py
```

## Features

✅ YouTube video download
✅ Multi-segment cutting
✅ 3 speed modes (Fast/Balanced/Accurate)
✅ Audio on/off
✅ Google Drive auto-upload
✅ Interactive CLI
✅ GUI interface
✅ Progress tracking

## Links

- Documentation: [README.md](README.md)
- Performance Guide: [PERFORMANCE.md](PERFORMANCE.md)
- Build Windows EXE: [BUILD_WINDOWS.md](BUILD_WINDOWS.md)

---

**Happy Video Editing! 🎬✨**
