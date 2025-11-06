# 🎬 Video Cutter Tool - Công cụ Cắt và Ghép Video

Công cụ Python đơn giản giúp bạn cắt nhiều đoạn từ video dài và tự động ghép chúng lại với nhau.

**🎨 Có 2 cách sử dụng:**
- **GUI (Giao diện đồ họa)** - Dễ dùng, thân thiện cho người mới
- **CLI (Command Line)** - Linh hoạt, mạnh mẽ cho người có kinh nghiệm

## ✨ Tính năng

- ✂️ **Cắt nhiều đoạn** từ một video dài
- 🔗 **Tự động ghép** các đoạn lại với nhau
- ⏱️ **Định dạng thời gian linh hoạt**: hỗ trợ MM:SS và HH:MM:SS
- 📊 **Hiển thị tiến trình** rõ ràng
- 🪟 **Giao diện đồ họa** cho Windows (và các hệ điều hành khác)
- 🎯 **Dễ sử dụng** với cả GUI và command-line
- 🔊 **Tùy chọn âm thanh**: Bật/tắt audio theo ý muốn
- ⚡ **3 chế độ tốc độ**: Fast (10-20x), Balanced (3-4x), Accurate
- 📥 **Tải video từ YouTube**: Tích hợp sẵn YouTube downloader

## 📋 Yêu cầu

- Python 3.6+
- ffmpeg
- yt-dlp (tùy chọn - chỉ cần nếu muốn tải video từ YouTube)

### Cài đặt ffmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
- Tải từ [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
- Giải nén và thêm vào PATH

### Cài đặt yt-dlp (Tùy chọn - cho tính năng YouTube)

```bash
pip install yt-dlp
```

## 🚀 Cách sử dụng

### 🪟 Phương pháp 1: Giao diện đồ họa (GUI) - KHUYẾN NGHỊ

**Cách đơn giản nhất! Dành cho mọi người.**

#### Chạy ứng dụng GUI:

```bash
python video_cutter_gui.py
```

#### Các bước sử dụng:

**Tùy chọn A: Tải video từ YouTube (nếu cần)**

0. **📥 Tải từ YouTube** (Tùy chọn):
   - Nhập URL YouTube vào ô "YouTube URL"
   - Nhấn "⬇️ Tải xuống"
   - Video sẽ tự động điền vào mục "Video đầu vào" sau khi tải xong

**Hoặc Tùy chọn B: Chọn video có sẵn**

1. **📹 Chọn video đầu vào**: Nhấn nút "Chọn Video" để chọn file video dài của bạn

**Sau đó, tiếp tục với các bước sau:**

2. **✂️ Nhập đoạn cắt**: Gõ các đoạn cần cắt theo định dạng, hoặc nhấn "Dán ví dụ mẫu"
   - Ví dụ: `03:05-03:10|40:05-40:10|1:03:05-1:04:05`
3. **✓ Kiểm tra**: Nhấn "Kiểm tra định dạng" để xem trước kết quả
4. **💾 Chọn nơi lưu**: Nhấn "Chọn nơi lưu" để chọn vị trí và tên file đầu ra
5. **⚙️ Chọn chế độ**: Chọn Fast/Balanced/Accurate (mặc định: Balanced)
6. **🔊 Tùy chọn âm thanh**: Tích vào "🔇 Tắt âm thanh" nếu muốn video không có tiếng
7. **🚀 Bắt đầu**: Nhấn "BẮT ĐẦU CẮT VIDEO" và chờ hoàn thành!

#### Screenshots:

```
┌─────────────────────────────────────────────────┐
│  🎬 VIDEO CUTTER TOOL                           │
│  Công cụ cắt và ghép video                      │
├─────────────────────────────────────────────────┤
│  📹 Video đầu vào:                              │
│  [C:\Videos\video.mp4        ] [Chọn Video]    │
│                                                  │
│  ✂️ Đoạn cần cắt:                               │
│  ┌────────────────────────────────────────────┐ │
│  │ 03:05-03:10|40:05-40:10|1:03:05-1:04:05   │ │
│  └────────────────────────────────────────────┘ │
│  [📝 Dán ví dụ mẫu] [✓ Kiểm tra định dạng]     │
│                                                  │
│  💾 Video đầu ra:                               │
│  [C:\Videos\output.mp4       ] [Chọn nơi lưu]  │
│                                                  │
│  📊 Thông tin:                                  │
│  ┌────────────────────────────────────────────┐ │
│  │ ✅ Định dạng hợp lệ!                       │ │
│  │ Tổng số đoạn: 3                            │ │
│  │ Tổng thời lượng: 1 phút 10 giây           │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  [🚀 BẮT ĐẦU CẮT VIDEO] [❌ Hủy] [🗑️ Xóa tất cả] │
└─────────────────────────────────────────────────┘
```

#### Tạo file .exe cho Windows:

Xem hướng dẫn chi tiết trong [BUILD_WINDOWS.md](BUILD_WINDOWS.md)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="VideoCutter" video_cutter_gui.py
```

File EXE sẽ nằm trong thư mục `dist/VideoCutter.exe`

---

### ⌨️ Phương pháp 2: Command Line (CLI)

### Cú pháp cơ bản

```bash
python video_cutter.py -i <video_đầu_vào> -s "<các_đoạn_cắt>" -o <video_đầu_ra>
```

### Định dạng thời gian

- **MM:SS** - Ví dụ: `03:05` (3 phút 5 giây)
- **HH:MM:SS** - Ví dụ: `1:03:05` (1 giờ 3 phút 5 giây)

### Định dạng đoạn cắt

Các đoạn được phân cách bằng dấu `|`:

```
start1-end1|start2-end2|start3-end3
```

### ⚡ Chế độ xử lý (Performance Modes)

Tool hỗ trợ 3 chế độ tốc độ khác nhau:

| Chế độ | Tốc độ | Chính xác | Khi nào dùng |
|--------|--------|-----------|--------------|
| 🚀 **Fast** | Rất nhanh (10-20x) | ⚠️ ±1-2s | Test nhanh, video không quan trọng |
| ⚡ **Balanced** | Nhanh (3-4x) | ✅ 100% | **KHUYẾN NGHỊ** - Dùng cho hầu hết trường hợp |
| 🎯 **Accurate** | Chậm nhất | ✅ 100% | Video CỰC quan trọng |

**Ví dụ sử dụng với mode:**

```bash
# Fast mode - Nhanh nhất
python video_cutter.py -i input.mp4 -s "segments" -o output.mp4 --mode fast

# Balanced mode - Mặc định (khuyến nghị)
python video_cutter.py -i input.mp4 -s "segments" -o output.mp4

# Accurate mode - Chính xác nhất
python video_cutter.py -i input.mp4 -s "segments" -o output.mp4 --mode accurate
```

### 🔊 Tùy chọn âm thanh

Bật hoặc tắt âm thanh cho video đầu ra:

```bash
# Video không có âm thanh (silent)
python video_cutter.py -i input.mp4 -s "segments" -o output.mp4 --no-audio

# Video giữ nguyên âm thanh (mặc định)
python video_cutter.py -i input.mp4 -s "segments" -o output.mp4

# Kết hợp: Fast mode + No audio
python video_cutter.py -i input.mp4 -s "segments" -o output.mp4 --mode fast --no-audio
```

**Khi nào dùng `--no-audio`:**
- Tạo video để thêm nhạc nền sau
- Video GIF-style không cần âm thanh
- Giảm kích thước file
- Tạo video highlight im lặng

📖 **Chi tiết về hiệu suất**: Xem [PERFORMANCE.md](PERFORMANCE.md)

## 📝 Ví dụ

### Ví dụ 1: Cắt 3 đoạn từ video dài

```bash
python video_cutter.py \
  -i video_dai.mp4 \
  -s "03:05-03:10|40:05-40:10|1:03:05-1:04:05" \
  -o video_ngan.mp4
```

**Kết quả:**
- Đoạn 1: từ 3:05 đến 3:10 (5 giây)
- Đoạn 2: từ 40:05 đến 40:10 (5 giây)
- Đoạn 3: từ 1:03:05 đến 1:04:05 (60 giây)
- **Tổng:** Video mới dài 1 phút 10 giây

### Ví dụ 2: Tạo video highlight

```bash
python video_cutter.py \
  -i webinar_full.mp4 \
  -s "00:30-01:00|15:20-16:45|45:00-47:30" \
  -o webinar_highlights.mp4
```

### Ví dụ 3: Chỉ định thư mục tạm

```bash
python video_cutter.py \
  -i input.mp4 \
  -s "10:00-10:30|20:00-20:45" \
  -o output.mp4 \
  -t my_temp_folder
```

### Ví dụ 4: Tải video từ YouTube (CLI)

```bash
# Tải video từ YouTube
python youtube_downloader.py https://www.youtube.com/watch?v=VIDEO_ID

# Tải và chỉ định tên file
python youtube_downloader.py https://www.youtube.com/watch?v=VIDEO_ID -o my_video.mp4

# Tải vào thư mục cụ thể
python youtube_downloader.py https://www.youtube.com/watch?v=VIDEO_ID -d ./my_videos

# Chỉ xem thông tin video (không tải)
python youtube_downloader.py https://www.youtube.com/watch?v=VIDEO_ID --info
```

### Ví dụ 5: Workflow hoàn chỉnh (YouTube → Cắt)

```bash
# Bước 1: Tải video từ YouTube
python youtube_downloader.py https://www.youtube.com/watch?v=VIDEO_ID -o youtube_video.mp4

# Bước 2: Cắt video vừa tải
python video_cutter.py \
  -i downloads/youtube_video.mp4 \
  -s "00:30-01:00|05:00-05:30|10:00-11:00" \
  -o highlights.mp4 \
  --mode fast \
  --no-audio
```

**💡 Mẹo**: Dùng GUI để làm tất cả trong một bước - không cần chạy nhiều lệnh!

## 🎯 Các tham số

| Tham số | Bắt buộc | Mô tả |
|---------|----------|-------|
| `-i, --input` | ✅ | Đường dẫn video đầu vào |
| `-s, --segments` | ✅ | Các đoạn cần cắt (format: start-end\|start-end\|...) |
| `-o, --output` | ✅ | Đường dẫn video đầu ra |
| `-t, --temp-dir` | ❌ | Thư mục tạm (mặc định: temp_segments) |

## 💡 Mẹo sử dụng

1. **Độ chính xác**: Tool sử dụng encoding lại để đảm bảo độ chính xác của thời gian cắt
2. **Định dạng video**: Đầu ra sẽ là MP4 với codec H.264 và AAC
3. **File tạm**: Các file tạm sẽ tự động được xóa sau khi hoàn thành
4. **Thời gian xử lý**: Phụ thuộc vào độ dài video và số lượng đoạn cần cắt

## 📊 Output mẫu

```
🎬 Bắt đầu cắt video từ: video_dai.mp4
📊 Tổng số đoạn cần cắt: 3

✂️  Đoạn 1/3: 03:05.000 → 03:10.000 (Độ dài: 00:05.000)
✂️  Đoạn 2/3: 40:05.000 → 40:10.000 (Độ dài: 00:05.000)
✂️  Đoạn 3/3: 01:03:05.000 → 01:04:05.000 (Độ dài: 01:00.000)

✅ Đã cắt xong 3 đoạn
⏱️  Tổng thời lượng video mới: 01:10.000

🔗 Đang ghép các đoạn lại với nhau...
✨ Hoàn thành! Video đã được lưu tại: video_ngan.mp4

🧹 Đã xóa các file tạm
```

## 🛠️ Xử lý lỗi

### "ffmpeg chưa được cài đặt"
```bash
# Kiểm tra ffmpeg
ffmpeg -version

# Nếu chưa có, cài đặt theo hướng dẫn ở trên
```

### "Không tìm thấy file video"
- Kiểm tra đường dẫn file đầu vào
- Sử dụng đường dẫn tuyệt đối nếu cần

### "Thời gian kết thúc phải lớn hơn thời gian bắt đầu"
- Kiểm tra lại định dạng các đoạn cắt
- Đảm bảo end_time > start_time

## 📄 License

MIT License - Tự do sử dụng và chỉnh sửa

## 🤝 Đóng góp

Mọi đóng góp đều được hoan nghênh! Hãy tạo issue hoặc pull request.

## 📮 Liên hệ

Nếu có vấn đề hoặc câu hỏi, vui lòng tạo issue trên GitHub.

---

**Happy Video Cutting! 🎬✨**
