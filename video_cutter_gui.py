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
from video_cutter import parse_segments, parse_time_to_seconds, format_duration, check_ffmpeg
import subprocess


class VideoCutterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 Video Cutter Tool - Công cụ Cắt Video")
        self.root.geometry("800x700")
        self.root.resizable(True, True)

        # Variables
        self.input_video_path = tk.StringVar()
        self.output_video_path = tk.StringVar()
        self.segments_text = tk.StringVar()
        self.is_processing = False

        # Setup UI
        self.setup_ui()

        # Check ffmpeg on startup
        self.root.after(500, self.check_ffmpeg_installed)

    def setup_ui(self):
        """Tạo giao diện người dùng"""

        # Main container với padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

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

        # ===== INPUT VIDEO =====
        row = 1
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

        # ===== PREVIEW INFO =====
        row += 2
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

    def start_processing(self):
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

        # Start processing in background thread
        self.is_processing = True
        self.process_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.progress_bar.start(10)
        self.progress_label.config(text="⏳ Đang xử lý...")

        # Run in thread
        thread = threading.Thread(
            target=self.process_video,
            args=(input_path, segments, output_path),
            daemon=True
        )
        thread.start()

    def process_video(self, input_path, segments, output_path):
        """Xử lý video (chạy trong thread riêng)"""
        try:
            temp_dir = "temp_segments_gui"
            os.makedirs(temp_dir, exist_ok=True)

            segment_files = []
            total_segments = len(segments)

            self.update_progress(f"📹 Đang cắt {total_segments} đoạn video...")

            # Cut segments
            for idx, (start_time, end_time) in enumerate(segments, 1):
                if not self.is_processing:
                    self.update_progress("❌ Đã hủy")
                    return

                duration = end_time - start_time
                segment_file = os.path.join(temp_dir, f"segment_{idx:03d}.mp4")
                segment_files.append(segment_file)

                self.update_progress(
                    f"✂️  Đang cắt đoạn {idx}/{total_segments}: "
                    f"{format_duration(start_time)} → {format_duration(end_time)}"
                )

                cmd = [
                    'ffmpeg',
                    '-ss', str(start_time),
                    '-i', input_path,
                    '-t', str(duration),
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-strict', 'experimental',
                    '-y',
                    segment_file
                ]

                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                if result.returncode != 0:
                    raise RuntimeError(f"Lỗi khi cắt đoạn {idx}")

            # Concatenate
            self.update_progress("🔗 Đang ghép các đoạn lại với nhau...")

            concat_file = os.path.join(temp_dir, "concat_list.txt")
            with open(concat_file, 'w') as f:
                for segment_file in segment_files:
                    abs_path = os.path.abspath(segment_file)
                    f.write(f"file '{abs_path}'\n")

            concat_cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-c', 'copy',
                '-y',
                output_path
            ]

            result = subprocess.run(concat_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode != 0:
                raise RuntimeError("Lỗi khi ghép video")

            # Cleanup
            import shutil
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

            # Success
            self.root.after(0, lambda: self.processing_complete(output_path))

        except Exception as e:
            self.root.after(0, lambda: self.processing_error(str(e)))

    def update_progress(self, message):
        """Cập nhật progress label"""
        self.root.after(0, lambda: self.progress_label.config(text=message))

    def processing_complete(self, output_path):
        """Xử lý hoàn thành"""
        self.is_processing = False
        self.progress_bar.stop()
        self.progress_label.config(text="✅ Hoàn thành!")
        self.process_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")

        result = messagebox.showinfo(
            "Thành công",
            f"✨ Video đã được cắt và lưu thành công!\n\n"
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
        self.cancel_btn.config(state="disabled")

        messagebox.showerror("Lỗi", f"❌ Có lỗi xảy ra:\n\n{error_message}")

    def cancel_processing(self):
        """Hủy xử lý"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn hủy?"):
            self.is_processing = False
            self.progress_bar.stop()
            self.progress_label.config(text="❌ Đã hủy")
            self.process_btn.config(state="normal")
            self.cancel_btn.config(state="disabled")


def main():
    """Main function"""
    root = tk.Tk()
    app = VideoCutterGUI(root)

    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()


if __name__ == '__main__':
    main()
