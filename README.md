# 🎬 Video Cutter Tool - Công cụ Cắt và Ghép Video

Công cụ Python đơn giản giúp bạn cắt nhiều đoạn từ video dài và tự động ghép chúng lại với nhau.

## ✨ Tính năng

- ✂️ **Cắt nhiều đoạn** từ một video dài
- 🔗 **Tự động ghép** các đoạn lại với nhau
- ⏱️ **Định dạng thời gian linh hoạt**: hỗ trợ MM:SS và HH:MM:SS
- 📊 **Hiển thị tiến trình** rõ ràng
- 🎯 **Dễ sử dụng** với giao diện command-line đơn giản

## 📋 Yêu cầu

- Python 3.6+
- ffmpeg

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

## 🚀 Cách sử dụng

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
