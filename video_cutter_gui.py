#!/usr/bin/env python3
"""
Video Cutter GUI - Giao diện đồ họa cho công cụ cắt video
GUI Application for Video Cutting Tool
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from pathlib import Path

# Import functions từ video_cutter
from video_cutter import (
    parse_segments, parse_time_to_seconds, format_duration,
    check_ffmpeg, cut_video_segments
)
import subprocess

# Import YouTube downloader (optional)
try:
    from youtube_downloader import YouTubeDownloader
    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False

# Import Rclone uploader (optional)
try:
    from rclone_uploader import RcloneUploader
    RCLONE_AVAILABLE = True
except ImportError:
    RCLONE_AVAILABLE = False


class VideoCutterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 Video Cutter Tool - Công cụ Cắt Video")

        # Get screen size and set responsive window size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Set window size to 80% of screen, max 900x800
        window_width = min(900, int(screen_width * 0.8))
        window_height = min(800, int(screen_height * 0.85))

        # Center window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(True, True)

        # Set minimum size
        self.root.minsize(750, 600)

        # Variables
        self.input_video_path = tk.StringVar()
        self.output_video_path = tk.StringVar()
        self.segments_text = tk.StringVar()
        self.processing_mode = tk.StringVar(value="balanced")  # Default: balanced
        self.volume = tk.IntVar(value=100)  # Default: 100% (original volume)
        self.is_processing = False

        # YouTube downloader variables
        self.youtube_url = tk.StringVar()
        self.is_downloading = False
        self.youtube_downloader = YouTubeDownloader(output_path="downloads") if YOUTUBE_AVAILABLE else None

        # Rclone variables
        self.rclone_config_file = "rclone_config.conf"
        self.rclone_config_content = None
        self.remote_path = tk.StringVar(value="")  # Remote folder path
        self.load_rclone_config()

        # Setup UI
        self.setup_ui()

        # Check ffmpeg on startup
        self.root.after(500, self.check_ffmpeg_installed)

    def setup_ui(self):
        """Tạo giao diện người dùng"""

        # Configure root grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Create main container with canvas and scrollbar
        container = ttk.Frame(self.root)
        container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        # Create canvas
        self.canvas = tk.Canvas(container, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create scrollbar
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Create frame inside canvas
        main_frame = ttk.Frame(self.canvas, padding="10")
        self.canvas_frame = self.canvas.create_window((0, 0), window=main_frame, anchor=tk.NW)

        # Configure main_frame
        main_frame.columnconfigure(1, weight=1)

        # Bind events for scrolling
        def _on_frame_configure(event):
            """Reset scroll region when frame size changes"""
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        def _on_canvas_configure(event):
            """Resize frame to match canvas width"""
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas_frame, width=canvas_width)

        def _on_mousewheel(event):
            """Scroll with mousewheel"""
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _on_enter(event):
            """Bind mousewheel when mouse enters"""
            if sys.platform == "win32":
                self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
            else:
                self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
                self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

        def _on_leave(event):
            """Unbind mousewheel when mouse leaves"""
            if sys.platform == "win32":
                self.canvas.unbind_all("<MouseWheel>")
            else:
                self.canvas.unbind_all("<Button-4>")
                self.canvas.unbind_all("<Button-5>")

        main_frame.bind("<Configure>", _on_frame_configure)
        self.canvas.bind("<Configure>", _on_canvas_configure)
        self.canvas.bind("<Enter>", _on_enter)
        self.canvas.bind("<Leave>", _on_leave)

        # ===== HEADER =====
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        title_label = ttk.Label(
            header_frame,
            text="🎬 VIDEO CUTTER TOOL",
            font=("Arial", 18, "bold")
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            header_frame,
            text="Công cụ cắt và ghép video - Video Cutting & Concatenation Tool",
            font=("Arial", 10)
        )
        subtitle_label.pack()

        row = 1

        # ===== YOUTUBE DOWNLOAD =====
        if YOUTUBE_AVAILABLE:
            youtube_frame = ttk.LabelFrame(main_frame, text="📥 Tải video từ YouTube (Tùy chọn)", padding="10")
            youtube_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
            youtube_frame.columnconfigure(0, weight=1)

            # YouTube URL input
            url_frame = ttk.Frame(youtube_frame)
            url_frame.pack(fill=tk.X, pady=(0, 5))
            url_frame.columnconfigure(0, weight=1)

            ttk.Label(url_frame, text="🔗 YouTube URL:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

            url_entry_frame = ttk.Frame(url_frame)
            url_entry_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
            url_entry_frame.columnconfigure(0, weight=1)

            self.youtube_url_entry = ttk.Entry(url_entry_frame, textvariable=self.youtube_url)
            self.youtube_url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

            self.download_btn = ttk.Button(url_entry_frame, text="⬇️ Tải xuống", command=self.start_youtube_download)
            self.download_btn.grid(row=0, column=1)

            # YouTube download status
            self.youtube_status = tk.StringVar(value="Nhập URL YouTube và nhấn Tải xuống")
            youtube_status_label = ttk.Label(youtube_frame, textvariable=self.youtube_status, font=("Arial", 8), foreground="gray")
            youtube_status_label.pack(anchor=tk.W, pady=(5, 0))

            row += 1

        # ===== INPUT VIDEO =====
        ttk.Label(main_frame, text="📹 Video đầu vào:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=(10, 5)
        )

        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=row+1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)

        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_video_path, state="readonly")
        self.input_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        browse_input_btn = ttk.Button(input_frame, text="Chọn Video", command=self.browse_input_video)
        browse_input_btn.grid(row=0, column=1)

        # ===== SEGMENTS INPUT =====
        row += 2
        ttk.Label(main_frame, text="✂️ Đoạn cần cắt:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=(10, 5)
        )

        # Info label
        info_label = ttk.Label(
            main_frame,
            text="Định dạng: start1-end1|start2-end2|start3-end3 (Ví dụ: 03:05-03:10|40:05-40:10|1:03:05-1:04:05)",
            font=("Arial", 8),
            foreground="gray"
        )
        info_label.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=(10, 5))

        # Segments text area
        row += 1
        self.segments_entry = scrolledtext.ScrolledText(
            main_frame,
            height=4,
            width=60,
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        self.segments_entry.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))

        # Example button
        example_btn = ttk.Button(
            main_frame,
            text="📝 Dán ví dụ mẫu",
            command=self.insert_example
        )
        example_btn.grid(row=row+1, column=0, sticky=tk.W, pady=(0, 10))

        # Validate button
        validate_btn = ttk.Button(
            main_frame,
            text="✓ Kiểm tra định dạng",
            command=self.validate_segments
        )
        validate_btn.grid(row=row+1, column=1, sticky=tk.W, pady=(0, 10), padx=(10, 0))

        # ===== OUTPUT VIDEO =====
        row += 2
        ttk.Label(main_frame, text="💾 Video đầu ra:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=(10, 5)
        )

        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=row+1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)

        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_video_path)
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        browse_output_btn = ttk.Button(output_frame, text="Chọn nơi lưu", command=self.browse_output_video)
        browse_output_btn.grid(row=0, column=1)

        # ===== PROCESSING MODE =====
        row += 2
        ttk.Label(main_frame, text="⚙️ Chế độ xử lý:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=(10, 5)
        )

        mode_frame = ttk.LabelFrame(main_frame, text="Chọn chế độ tốc độ", padding="10")
        mode_frame.grid(row=row+1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # Radio buttons for mode selection
        ttk.Radiobutton(
            mode_frame,
            text="🚀 Fast - Rất nhanh (có thể sai lệch 1-2s, dùng khi không cần chính xác tuyệt đối)",
            variable=self.processing_mode,
            value="fast"
        ).pack(anchor=tk.W, pady=2)

        ttk.Radiobutton(
            mode_frame,
            text="⚡ Balanced - Cân bằng (nhanh + chính xác, KHUYẾN NGHỊ)",
            variable=self.processing_mode,
            value="balanced"
        ).pack(anchor=tk.W, pady=2)

        ttk.Radiobutton(
            mode_frame,
            text="🎯 Accurate - Chính xác tuyệt đối (chậm nhất, cho video quan trọng)",
            variable=self.processing_mode,
            value="accurate"
        ).pack(anchor=tk.W, pady=2)

        # Mode explanation
        mode_explain = ttk.Label(
            mode_frame,
            text="💡 Mẹo: Dùng Fast để kiểm tra nhanh, Balanced cho hầu hết trường hợp, Accurate cho video quan trọng",
            font=("Arial", 8),
            foreground="gray"
        )
        mode_explain.pack(anchor=tk.W, pady=(5, 0))

        # ===== VOLUME CONTROL =====
        row += 2
        volume_frame = ttk.LabelFrame(main_frame, text="🔊 Điều chỉnh âm lượng", padding="10")
        volume_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 10))

        volume_info_frame = ttk.Frame(volume_frame)
        volume_info_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(volume_info_frame, text="0% = Tắt | 100% = Giữ nguyên | 200% = Tăng 2x").pack(side=tk.LEFT)
        self.volume_label = ttk.Label(volume_info_frame, text="100%", font=("Arial", 10, "bold"))
        self.volume_label.pack(side=tk.RIGHT)

        volume_slider = ttk.Scale(
            volume_frame,
            from_=0,
            to=200,
            orient=tk.HORIZONTAL,
            variable=self.volume,
            command=self.update_volume_label
        )
        volume_slider.pack(fill=tk.X, pady=(0, 5))

        # Preset buttons
        preset_frame = ttk.Frame(volume_frame)
        preset_frame.pack(fill=tk.X)

        ttk.Button(preset_frame, text="Tắt (0%)", command=lambda: self.set_volume(0)).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="50%", command=lambda: self.set_volume(50)).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="100%", command=lambda: self.set_volume(100)).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="150%", command=lambda: self.set_volume(150)).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="200%", command=lambda: self.set_volume(200)).pack(side=tk.LEFT, padx=2)

        # ===== PREVIEW INFO =====
        row += 1
        ttk.Label(main_frame, text="📊 Thông tin:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=(10, 5)
        )

        # Info text area
        row += 1
        self.info_text = scrolledtext.ScrolledText(
            main_frame,
            height=8,
            width=60,
            font=("Consolas", 9),
            wrap=tk.WORD,
            state="disabled"
        )
        self.info_text.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # ===== RCLONE UPLOAD =====
        row += 1
        rclone_frame = ttk.LabelFrame(main_frame, text="📤 Upload lên Google Drive (Rclone)", padding="10")
        rclone_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 10))
        rclone_frame.columnconfigure(0, weight=1)

        # Status label
        self.rclone_status = tk.StringVar(value="⚠️ Chưa cấu hình rclone" if not self.rclone_config_content else "✅ Đã cấu hình rclone")
        status_label = ttk.Label(rclone_frame, textvariable=self.rclone_status, font=("Arial", 9))
        status_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        # Config button
        self.config_btn = ttk.Button(
            rclone_frame,
            text="⚙️ Cấu hình rclone" if not self.rclone_config_content else "✏️ Chỉnh sửa cấu hình",
            command=self.show_rclone_config_dialog
        )
        self.config_btn.grid(row=0, column=1, sticky=tk.E, pady=(0, 5))

        # Remote path
        path_frame = ttk.Frame(rclone_frame)
        path_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        path_frame.columnconfigure(1, weight=1)

        ttk.Label(path_frame, text="📁 Thư mục trên Drive:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        remote_entry = ttk.Entry(path_frame, textvariable=self.remote_path)
        remote_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        ttk.Label(
            rclone_frame,
            text="💡 Để trống = thư mục gốc",
            font=("Arial", 8),
            foreground="gray"
        ).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(2, 0))

        # ===== PROGRESS BAR =====
        row += 1
        self.progress_label = ttk.Label(main_frame, text="Sẵn sàng", font=("Arial", 9))
        self.progress_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))

        row += 1
        self.progress_bar = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=400
        )
        self.progress_bar.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # ===== ACTION BUTTONS =====
        row += 1
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=(10, 0))

        self.process_btn = ttk.Button(
            button_frame,
            text="🚀 BẮT ĐẦU CẮT VIDEO",
            command=self.start_processing,
            style="Accent.TButton"
        )
        self.process_btn.pack(side=tk.LEFT, padx=5)

        self.process_upload_btn = ttk.Button(
            button_frame,
            text="📤 CẮT VÀ UPLOAD LÊN DRIVE",
            command=self.start_processing_with_upload,
            style="Accent.TButton"
        )
        self.process_upload_btn.pack(side=tk.LEFT, padx=5)

        self.cancel_btn = ttk.Button(
            button_frame,
            text="❌ Hủy",
            command=self.cancel_processing,
            state="disabled"
        )
        self.cancel_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(
            button_frame,
            text="🗑️ Xóa tất cả",
            command=self.clear_all
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        # Configure style for accent button
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Arial", 10, "bold"))

        # Initial info message
        self.update_info_text("✨ Chào mừng đến với Video Cutter Tool!\n\n"
                             "📝 Hướng dẫn sử dụng:\n"
                             "1. Chọn video đầu vào\n"
                             "2. Nhập các đoạn cần cắt (hoặc dùng ví dụ mẫu)\n"
                             "3. Chọn nơi lưu video đầu ra\n"
                             "4. Nhấn 'Bắt đầu cắt video'\n\n"
                             "💡 Mẹo: Nhấn 'Kiểm tra định dạng' để xem trước kết quả!")

    def check_ffmpeg_installed(self):
        """Kiểm tra xem ffmpeg đã được cài đặt chưa"""
        if not check_ffmpeg():
            messagebox.showwarning(
                "Thiếu ffmpeg",
                "⚠️ Không tìm thấy ffmpeg!\n\n"
                "Vui lòng cài đặt ffmpeg trước khi sử dụng:\n\n"
                "• Windows: Tải từ https://ffmpeg.org/download.html\n"
                "• Ubuntu: sudo apt-get install ffmpeg\n"
                "• macOS: brew install ffmpeg"
            )

    def browse_input_video(self):
        """Chọn video đầu vào"""
        filename = filedialog.askopenfilename(
            title="Chọn video đầu vào",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.webm"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.input_video_path.set(filename)
            # Auto-suggest output filename
            if not self.output_video_path.get():
                input_path = Path(filename)
                output_name = input_path.stem + "_cut" + input_path.suffix
                output_path = input_path.parent / output_name
                self.output_video_path.set(str(output_path))

    def browse_output_video(self):
        """Chọn nơi lưu video đầu ra"""
        filename = filedialog.asksaveasfilename(
            title="Chọn nơi lưu video",
            defaultextension=".mp4",
            filetypes=[
                ("MP4 files", "*.mp4"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.output_video_path.set(filename)

    def insert_example(self):
        """Chèn ví dụ mẫu"""
        example = "03:05-03:10|40:05-40:10|1:03:05-1:04:05"
        self.segments_entry.delete("1.0", tk.END)
        self.segments_entry.insert("1.0", example)

    def validate_segments(self):
        """Kiểm tra và hiển thị thông tin các đoạn"""
        segments_str = self.segments_entry.get("1.0", tk.END).strip()

        if not segments_str:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập các đoạn cần cắt!")
            return

        try:
            segments = parse_segments(segments_str)

            # Build info message
            info = "✅ Định dạng hợp lệ!\n\n"
            info += f"📊 Tổng số đoạn: {len(segments)}\n"
            info += "━" * 50 + "\n\n"

            total_duration = 0
            for idx, (start, end) in enumerate(segments, 1):
                duration = end - start
                total_duration += duration
                info += f"✂️ Đoạn {idx}: {format_duration(start)} → {format_duration(end)}\n"
                info += f"   Độ dài: {format_duration(duration)}\n\n"

            info += "━" * 50 + "\n"
            info += f"⏱️  Tổng thời lượng video mới: {format_duration(total_duration)}\n"
            info += f"   ({total_duration:.1f} giây = {total_duration/60:.2f} phút)"

            self.update_info_text(info)

        except Exception as e:
            messagebox.showerror("Lỗi định dạng", f"❌ Định dạng không hợp lệ:\n\n{str(e)}")

    def update_info_text(self, text):
        """Cập nhật text trong info area"""
        self.info_text.config(state="normal")
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert("1.0", text)
        self.info_text.config(state="disabled")

    def clear_all(self):
        """Xóa tất cả các trường"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa tất cả?"):
            self.input_video_path.set("")
            self.output_video_path.set("")
            self.segments_entry.delete("1.0", tk.END)
            self.update_info_text("Đã xóa tất cả. Sẵn sàng bắt đầu mới!")

    # ===== VOLUME CONTROL METHODS =====

    def update_volume_label(self, value):
        """Update volume label when slider changes"""
        vol = int(float(value))
        self.volume_label.config(text=f"{vol}%")

    def set_volume(self, value):
        """Set volume to specific value"""
        self.volume.set(value)
        self.volume_label.config(text=f"{value}%")

    # ===== RCLONE METHODS =====

    def load_rclone_config(self):
        """Load rclone config from file"""
        try:
            if os.path.exists(self.rclone_config_file):
                with open(self.rclone_config_file, 'r') as f:
                    self.rclone_config_content = f.read()
        except Exception as e:
            print(f"Error loading rclone config: {e}")
            self.rclone_config_content = None

    def save_rclone_config(self, content):
        """Save rclone config to file"""
        try:
            with open(self.rclone_config_file, 'w') as f:
                f.write(content)
            self.rclone_config_content = content
            self.rclone_status.set("✅ Đã cấu hình rclone")
            self.config_btn.config(text="✏️ Chỉnh sửa cấu hình")
            return True
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu cấu hình:\n{e}")
            return False

    def show_rclone_config_dialog(self):
        """Show dialog to input/edit rclone config"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Cấu hình Rclone")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()

        # Header
        header = ttk.Label(
            dialog,
            text="📝 Cấu hình Rclone",
            font=("Arial", 14, "bold")
        )
        header.pack(pady=(10, 5))

        info = ttk.Label(
            dialog,
            text="Dán nội dung file rclone.conf của bạn vào đây:",
            font=("Arial", 10)
        )
        info.pack(pady=(0, 10))

        # Example
        example_frame = ttk.LabelFrame(dialog, text="Ví dụ:", padding="5")
        example_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        example_text = """[gdrive]
type = drive
scope = drive
token = {"access_token":"...","expiry":"2025-11-06T20:11:32+07:00"}
team_drive = """

        example_label = ttk.Label(
            example_frame,
            text=example_text,
            font=("Consolas", 8),
            foreground="gray"
        )
        example_label.pack()

        # Text area
        text_frame = ttk.Frame(dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        text_scroll = ttk.Scrollbar(text_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        config_text = tk.Text(
            text_frame,
            font=("Consolas", 9),
            wrap=tk.WORD,
            yscrollcommand=text_scroll.set
        )
        config_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scroll.config(command=config_text.yview)

        # Load existing config
        if self.rclone_config_content:
            config_text.insert("1.0", self.rclone_config_content)

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=(0, 10))

        def save_config():
            content = config_text.get("1.0", tk.END).strip()
            if not content:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập cấu hình rclone!")
                return

            # Basic validation
            if '[' not in content or 'type' not in content:
                messagebox.showwarning(
                    "Cảnh báo",
                    "Cấu hình không hợp lệ!\n\n"
                    "Cấu hình rclone cần có format:\n"
                    "[remote_name]\n"
                    "type = ...\n"
                    "..."
                )
                return

            if self.save_rclone_config(content):
                messagebox.showinfo("Thành công", "✅ Đã lưu cấu hình rclone!")
                dialog.destroy()

        ttk.Button(button_frame, text="💾 Lưu", command=save_config, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Hủy", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def start_processing_with_upload(self):
        """Start processing and upload to Drive"""
        # Check rclone config
        if not self.rclone_config_content:
            if messagebox.askyesno(
                "Chưa cấu hình rclone",
                "Bạn chưa cấu hình rclone!\n\n"
                "Bạn có muốn cấu hình ngay bây giờ không?"
            ):
                self.show_rclone_config_dialog()
            return

        # Start processing with upload flag
        self.start_processing(upload_to_drive=True)

    def start_processing(self, upload_to_drive=False):
        """Bắt đầu xử lý video"""
        # Validate inputs
        input_path = self.input_video_path.get()
        output_path = self.output_video_path.get()
        segments_str = self.segments_entry.get("1.0", tk.END).strip()

        if not input_path:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn video đầu vào!")
            return

        if not output_path:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn nơi lưu video đầu ra!")
            return

        if not segments_str:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập các đoạn cần cắt!")
            return

        if not os.path.exists(input_path):
            messagebox.showerror("Lỗi", f"Không tìm thấy file video:\n{input_path}")
            return

        # Parse segments
        try:
            segments = parse_segments(segments_str)
        except Exception as e:
            messagebox.showerror("Lỗi định dạng", f"Định dạng đoạn cắt không hợp lệ:\n\n{str(e)}")
            return

        # Get processing mode and volume
        mode = self.processing_mode.get()
        volume = self.volume.get()

        # Start processing in background thread
        self.is_processing = True
        self.process_btn.config(state="disabled")
        self.process_upload_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.progress_bar.start(10)

        mode_names = {
            'fast': '🚀 FAST MODE',
            'balanced': '⚡ BALANCED MODE',
            'accurate': '🎯 ACCURATE MODE'
        }
        volume_status = f"🔊 {volume}%"
        upload_status = " → 📤 Upload" if upload_to_drive else ""
        self.progress_label.config(text=f"⏳ Đang xử lý ({mode_names.get(mode, mode)} - {volume_status}{upload_status})...")

        # Run in thread
        thread = threading.Thread(
            target=self.process_video,
            args=(input_path, segments, output_path, mode, volume, upload_to_drive),
            daemon=True
        )
        thread.start()

    def process_video(self, input_path, segments, output_path, mode, volume, upload_to_drive):
        """Xử lý video (chạy trong thread riêng)"""
        try:
            # Progress callback để cập nhật UI
            def progress_callback(message):
                if self.is_processing:  # Chỉ update nếu chưa bị hủy
                    self.update_progress(message)

            # Sử dụng hàm cut_video_segments đã được tối ưu
            cut_video_segments(
                input_video=input_path,
                segments=segments,
                output_video=output_path,
                temp_dir="temp_segments_gui",
                mode=mode,
                max_workers=None,  # Auto-detect
                volume=volume,
                progress_callback=progress_callback
            )

            # Upload to Drive if requested
            if upload_to_drive and self.rclone_config_content:
                self.update_progress("📤 Đang upload lên Google Drive...")

                uploader = RcloneUploader(self.rclone_config_content)
                remotes = uploader.list_remotes()

                if remotes:
                    remote_name = remotes[0]
                    remote_path = self.remote_path.get()

                    success = uploader.upload_file(output_path, remote_name, remote_path)

                    if success:
                        self.update_progress("✅ Upload hoàn thành!")
                    else:
                        self.update_progress("⚠️ Upload thất bại")
                else:
                    self.update_progress("⚠️ Không tìm thấy remote trong config")

            # Success
            self.root.after(0, lambda: self.processing_complete(output_path, upload_to_drive))

        except Exception as e:
            self.root.after(0, lambda: self.processing_error(str(e)))

    def update_progress(self, message):
        """Cập nhật progress label"""
        self.root.after(0, lambda: self.progress_label.config(text=message))

    def processing_complete(self, output_path, uploaded=False):
        """Xử lý hoàn thành"""
        self.is_processing = False
        self.progress_bar.stop()
        self.progress_label.config(text="✅ Hoàn thành!")
        self.process_btn.config(state="normal")
        self.process_upload_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")

        upload_msg = "\n✅ Video đã được upload lên Google Drive!" if uploaded else ""
        result = messagebox.showinfo(
            "Thành công",
            f"✨ Video đã được cắt và lưu thành công!{upload_msg}\n\n"
            f"📁 Vị trí: {output_path}\n\n"
            f"Bạn có muốn mở thư mục chứa file không?"
        )

        # Open folder
        if messagebox.askyesno("Mở thư mục", "Mở thư mục chứa file?"):
            folder = os.path.dirname(output_path)
            if sys.platform == "win32":
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.run(["open", folder])
            else:
                subprocess.run(["xdg-open", folder])

    def processing_error(self, error_message):
        """Xử lý lỗi"""
        self.is_processing = False
        self.progress_bar.stop()
        self.progress_label.config(text="❌ Lỗi!")
        self.process_btn.config(state="normal")
        self.process_upload_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")

        messagebox.showerror("Lỗi", f"❌ Có lỗi xảy ra:\n\n{error_message}")

    def cancel_processing(self):
        """Hủy xử lý"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn hủy?"):
            self.is_processing = False
            self.progress_bar.stop()
            self.progress_label.config(text="❌ Đã hủy")
            self.process_btn.config(state="normal")
            self.process_upload_btn.config(state="normal")
            self.cancel_btn.config(state="disabled")

    # ===== YOUTUBE DOWNLOAD METHODS =====

    def start_youtube_download(self):
        """Bắt đầu tải video từ YouTube"""
        if not YOUTUBE_AVAILABLE:
            messagebox.showerror(
                "Thiếu thư viện",
                "yt-dlp chưa được cài đặt!\n\n"
                "Vui lòng cài đặt: pip install yt-dlp"
            )
            return

        url = self.youtube_url.get().strip()
        if not url:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập URL YouTube!")
            return

        # Validate URL
        if "youtube.com" not in url and "youtu.be" not in url:
            messagebox.showwarning("URL không hợp lệ", "Vui lòng nhập URL YouTube hợp lệ!")
            return

        # Start download in background
        self.is_downloading = True
        self.download_btn.config(state="disabled")
        self.youtube_status.set("⏳ Đang tải xuống...")

        thread = threading.Thread(
            target=self.download_youtube_video,
            args=(url,),
            daemon=True
        )
        thread.start()

    def download_youtube_video(self, url):
        """Tải video YouTube (chạy trong thread riêng)"""
        try:
            def progress_callback(message):
                if self.is_downloading:
                    self.root.after(0, lambda: self.youtube_status.set(message))

            success, file_path = self.youtube_downloader.download_video(
                url,
                progress_callback=progress_callback
            )

            if success and file_path:
                self.root.after(0, lambda: self.youtube_download_complete(file_path))
            else:
                self.root.after(0, lambda: self.youtube_download_error("Tải xuống thất bại"))

        except Exception as e:
            self.root.after(0, lambda: self.youtube_download_error(str(e)))

    def youtube_download_complete(self, file_path):
        """Xử lý khi tải YouTube hoàn thành"""
        self.is_downloading = False
        self.download_btn.config(state="normal")
        self.youtube_status.set(f"✅ Đã tải xong: {Path(file_path).name}")

        # Auto-fill input video path
        self.input_video_path.set(file_path)

        # Auto-suggest output filename
        if not self.output_video_path.get():
            input_path = Path(file_path)
            output_name = input_path.stem + "_cut" + input_path.suffix
            output_path = input_path.parent / output_name
            self.output_video_path.set(str(output_path))

        messagebox.showinfo(
            "Thành công",
            f"✅ Video đã được tải xuống!\n\n"
            f"📁 Vị trí: {file_path}\n\n"
            f"✂️ Video đã được tự động điền vào mục 'Video đầu vào'.\n"
            f"Bạn có thể tiếp tục nhập đoạn cắt và xử lý video."
        )

    def youtube_download_error(self, error_message):
        """Xử lý lỗi khi tải YouTube"""
        self.is_downloading = False
        self.download_btn.config(state="normal")
        self.youtube_status.set(f"❌ Lỗi: {error_message}")

        messagebox.showerror(
            "Lỗi tải xuống",
            f"❌ Không thể tải video:\n\n{error_message}\n\n"
            f"Vui lòng kiểm tra:\n"
            f"- URL có đúng không\n"
            f"- Kết nối internet\n"
            f"- ffmpeg đã được cài đặt"
        )


def main():
    """Main function"""
    root = tk.Tk()
    app = VideoCutterGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
