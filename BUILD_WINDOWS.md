# 🪟 Hướng dẫn tạo file EXE cho Windows

Tài liệu này hướng dẫn cách tạo file `.exe` độc lập cho Windows từ ứng dụng GUI Python.

## 📋 Yêu cầu

- Python 3.6 trở lên
- PyInstaller
- ffmpeg (sẽ cần cài riêng trên máy đích)

## 🚀 Bước 1: Cài đặt PyInstaller

```bash
pip install pyinstaller
```

## 🔨 Bước 2: Build file EXE

### Option 1: File EXE đơn (Recommended)

```bash
pyinstaller --onefile --windowed --name="VideoCutter" --icon=icon.ico video_cutter_gui.py
```

### Option 2: File EXE với thư mục

```bash
pyinstaller --windowed --name="VideoCutter" video_cutter_gui.py
```

### Giải thích tham số:

- `--onefile`: Tạo 1 file EXE duy nhất (dễ phân phối)
- `--windowed`: Không hiện cửa sổ console (cho GUI app)
- `--name="VideoCutter"`: Đặt tên cho file EXE
- `--icon=icon.ico`: Sử dụng icon tùy chỉnh (tùy chọn)

## 📦 Bước 3: Tìm file EXE

Sau khi build xong, file EXE sẽ nằm trong thư mục:

```
dist/VideoCutter.exe
```

## 🎯 Bước 4: Phân phối

### Cách 1: Chỉ file EXE (đơn giản nhất)

1. Copy file `VideoCutter.exe` từ thư mục `dist/`
2. Gửi cho người dùng
3. **Lưu ý**: Người dùng vẫn cần cài ffmpeg riêng

### Cách 2: Gói kèm ffmpeg (đầy đủ)

1. Tải ffmpeg Windows build: https://www.gyan.dev/ffmpeg/builds/
2. Giải nén và lấy file `ffmpeg.exe`
3. Tạo cấu trúc thư mục:
   ```
   VideoCutter/
   ├── VideoCutter.exe
   ├── ffmpeg.exe
   └── README.txt
   ```
4. Nén thành file ZIP để phân phối

### Tạo file README.txt cho người dùng:

```text
🎬 VIDEO CUTTER TOOL

Cách sử dụng:
1. Chạy VideoCutter.exe
2. Chọn video đầu vào
3. Nhập các đoạn cần cắt
4. Chọn nơi lưu file
5. Nhấn "Bắt đầu cắt video"

Yêu cầu:
- Windows 7 trở lên
- ffmpeg (đã được kèm theo nếu có file ffmpeg.exe)

Nếu báo lỗi thiếu ffmpeg:
- Đảm bảo ffmpeg.exe nằm cùng thư mục với VideoCutter.exe
- Hoặc cài ffmpeg vào system PATH
```

## 🔧 Advanced: Tích hợp ffmpeg vào EXE

### Bước 1: Download ffmpeg

```bash
# Tải ffmpeg static build cho Windows
# https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
```

### Bước 2: Tạo file spec tùy chỉnh

Tạo file `video_cutter_gui.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['video_cutter_gui.py'],
    pathex=[],
    binaries=[('ffmpeg.exe', '.')],  # Include ffmpeg
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VideoCutter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'  # Optional: add icon
)
```

### Bước 3: Build với spec file

```bash
pyinstaller video_cutter_gui.spec
```

## 🎨 Tùy chỉnh Icon (Optional)

### Tạo icon file

1. Tạo ảnh PNG kích thước 256x256 hoặc 512x512
2. Chuyển đổi sang ICO format:
   - Online: https://convertio.co/png-ico/
   - Tool: ImageMagick
   ```bash
   magick convert icon.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico
   ```

### Sử dụng icon

```bash
pyinstaller --onefile --windowed --icon=icon.ico video_cutter_gui.py
```

## 🐛 Troubleshooting

### Lỗi: "Failed to execute script"

**Nguyên nhân**: Thiếu dependencies

**Giải pháp**:
```bash
# Build với console để xem lỗi
pyinstaller --onefile video_cutter_gui.py

# Chạy và xem lỗi gì
dist/VideoCutter.exe
```

### Lỗi: "tkinter not found"

**Giải pháp**: Cài lại Python với tkinter support

### Lỗi: "ffmpeg not found" trong EXE

**Giải pháp**: Sửa code để tìm ffmpeg trong cùng thư mục với EXE

Thêm vào đầu file `video_cutter_gui.py`:

```python
import sys
import os

# Add ffmpeg to PATH if bundled
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = os.path.dirname(sys.executable)
    ffmpeg_path = os.path.join(application_path, 'ffmpeg.exe')
    if os.path.exists(ffmpeg_path):
        os.environ['PATH'] = application_path + os.pathsep + os.environ['PATH']
```

## 📊 Kích thước file

- **--onefile**: ~15-25 MB (1 file duy nhất)
- **--onedir**: ~30-40 MB (nhiều file trong thư mục)
- **Với ffmpeg**: Thêm ~70-100 MB

## 🔐 Bảo mật

### Antivirus có thể báo false positive

**Giải pháp**:
1. Code signing (nếu có certificate)
2. Whitelist trên VirusTotal
3. Hướng dẫn người dùng thêm exception

### Code signing (Advanced)

Cần certificate từ CA:

```bash
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com VideoCutter.exe
```

## 📝 Checklist hoàn chỉnh

- [ ] Cài PyInstaller
- [ ] Build file EXE
- [ ] Test trên máy khác (không có Python)
- [ ] Kiểm tra ffmpeg hoạt động
- [ ] Tạo thư mục phân phối
- [ ] Viết hướng dẫn sử dụng
- [ ] Nén thành ZIP
- [ ] Test trên Windows 10/11

## 🎉 Hoàn thành!

Giờ bạn có file EXE độc lập có thể chạy trên bất kỳ máy Windows nào!
