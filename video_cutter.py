#!/usr/bin/env python3
"""
Video Cutter Tool - Công cụ cắt và ghép video
Cho phép cắt nhiều đoạn từ video dài và ghép chúng lại với nhau
"""

import os
import sys
import subprocess
import argparse
from typing import List, Tuple, Optional
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


def parse_time_to_seconds(time_str: str) -> float:
    """
    Chuyển đổi thời gian từ format MM:SS hoặc HH:MM:SS sang giây

    Args:
        time_str: Chuỗi thời gian (vd: "03:05" hoặc "1:03:05")

    Returns:
        Số giây dạng float
    """
    parts = time_str.strip().split(':')

    if len(parts) == 2:  # MM:SS
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    elif len(parts) == 3:  # HH:MM:SS
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    else:
        raise ValueError(f"Định dạng thời gian không hợp lệ: {time_str}")


def parse_segments(segments_str: str) -> List[Tuple[float, float]]:
    """
    Phân tích chuỗi các đoạn cần cắt

    Args:
        segments_str: Chuỗi định dạng "03:05-03:10|40:05-40:10|1:03:05-1:04:05"

    Returns:
        List các tuple (start_time, end_time) tính bằng giây
    """
    segments = []

    # Tách các đoạn bằng dấu |
    segment_list = segments_str.split('|')

    for segment in segment_list:
        segment = segment.strip()
        if not segment:
            continue

        # Tách start và end time
        if '-' not in segment:
            raise ValueError(f"Đoạn không hợp lệ (thiếu dấu '-'): {segment}")

        start_str, end_str = segment.split('-', 1)
        start_time = parse_time_to_seconds(start_str)
        end_time = parse_time_to_seconds(end_str)

        if end_time <= start_time:
            raise ValueError(f"Thời gian kết thúc phải lớn hơn thời gian bắt đầu: {segment}")

        segments.append((start_time, end_time))

    return segments


def format_duration(seconds: float) -> str:
    """Chuyển đổi giây sang định dạng dễ đọc HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
    else:
        return f"{minutes:02d}:{secs:06.3f}"


def check_ffmpeg():
    """Kiểm tra xem ffmpeg đã được cài đặt chưa"""
    try:
        subprocess.run(['ffmpeg', '-version'],
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE,
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def cut_single_segment(input_video: str, start_time: float, end_time: float,
                      output_file: str, mode: str = "accurate") -> bool:
    """
    Cắt một đoạn video đơn lẻ

    Args:
        input_video: Đường dẫn video đầu vào
        start_time: Thời gian bắt đầu (giây)
        end_time: Thời gian kết thúc (giây)
        output_file: File đầu ra
        mode: Chế độ cắt ('fast', 'balanced', 'accurate')

    Returns:
        True nếu thành công, False nếu thất bại
    """
    duration = end_time - start_time

    # Xây dựng lệnh ffmpeg dựa trên mode
    if mode == "fast":
        # Fast mode: Copy codec (nhanh nhất, có thể không chính xác 1-2 giây)
        cmd = [
            'ffmpeg',
            '-ss', str(start_time),
            '-i', input_video,
            '-t', str(duration),
            '-c', 'copy',  # Copy codec - rất nhanh
            '-avoid_negative_ts', '1',  # Tránh timestamp âm
            '-y',
            output_file
        ]
    else:
        # Accurate/Balanced mode: Re-encode (chính xác tuyệt đối)
        cmd = [
            'ffmpeg',
            '-ss', str(start_time),
            '-i', input_video,
            '-t', str(duration),
            '-c:v', 'libx264',
            '-preset', 'medium',  # Cân bằng giữa tốc độ và chất lượng
            '-crf', '23',  # Constant Rate Factor (chất lượng tốt)
            '-c:a', 'aac',
            '-b:a', '128k',
            '-strict', 'experimental',
            '-y',
            output_file
        ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0


def cut_video_segments(input_video: str, segments: List[Tuple[float, float]],
                       output_video: str, temp_dir: str = "temp_segments",
                       mode: str = "balanced", max_workers: Optional[int] = None,
                       progress_callback=None):
    """
    Cắt và ghép các đoạn video với nhiều chế độ tốc độ

    Args:
        input_video: Đường dẫn video đầu vào
        segments: List các tuple (start_time, end_time)
        output_video: Đường dẫn video đầu ra
        temp_dir: Thư mục tạm để lưu các đoạn video
        mode: Chế độ xử lý
            - 'fast': Rất nhanh (copy codec) - có thể không chính xác 1-2 giây
            - 'balanced': Cân bằng (song song + re-encode) - nhanh và chính xác
            - 'accurate': Chính xác tuyệt đối (tuần tự + re-encode) - chậm nhất
        max_workers: Số luồng xử lý song song (None = auto, chỉ dùng cho balanced mode)
        progress_callback: Hàm callback để báo tiến trình (nhận message string)
    """
    def log(message):
        """Helper để in log hoặc gọi callback"""
        print(message)
        if progress_callback:
            progress_callback(message)

    # Kiểm tra ffmpeg
    if not check_ffmpeg():
        raise RuntimeError("ffmpeg chưa được cài đặt. Vui lòng cài đặt ffmpeg trước.")

    # Kiểm tra file đầu vào
    if not os.path.exists(input_video):
        raise FileNotFoundError(f"Không tìm thấy file video: {input_video}")

    # Tạo thư mục tạm
    os.makedirs(temp_dir, exist_ok=True)

    # Thông tin mode
    mode_info = {
        'fast': '🚀 FAST MODE (Rất nhanh - có thể sai lệch 1-2s)',
        'balanced': '⚡ BALANCED MODE (Nhanh + Chính xác)',
        'accurate': '🎯 ACCURATE MODE (Chính xác tuyệt đối)'
    }

    log(f"\n🎬 Bắt đầu cắt video từ: {input_video}")
    log(f"📊 Tổng số đoạn cần cắt: {len(segments)}")
    log(f"⚙️  Chế độ: {mode_info.get(mode, mode)}\n")

    segment_files = []
    total_duration = sum(end - start for start, end in segments)
    start_overall = time.time()

    try:
        if mode == "balanced":
            # BALANCED MODE: Xử lý song song
            if max_workers is None:
                max_workers = min(4, len(segments))  # Tối đa 4 luồng song song

            log(f"🔄 Đang cắt {len(segments)} đoạn song song với {max_workers} luồng...\n")

            # Chuẩn bị danh sách tasks
            tasks = []
            for idx, (start_time, end_time) in enumerate(segments, 1):
                segment_file = os.path.join(temp_dir, f"segment_{idx:03d}.mp4")
                segment_files.append(segment_file)
                tasks.append((idx, start_time, end_time, segment_file))

            # Xử lý song song
            completed = 0
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_task = {
                    executor.submit(cut_single_segment, input_video, start, end, out, mode): (idx, start, end)
                    for idx, start, end, out in tasks
                }

                for future in as_completed(future_to_task):
                    idx, start, end = future_to_task[future]
                    completed += 1
                    try:
                        success = future.result()
                        if success:
                            duration = end - start
                            log(f"✅ [{completed}/{len(segments)}] Đoạn {idx}: "
                                f"{format_duration(start)} → {format_duration(end)} "
                                f"(Độ dài: {format_duration(duration)})")
                        else:
                            raise RuntimeError(f"Lỗi khi cắt đoạn {idx}")
                    except Exception as e:
                        raise RuntimeError(f"Lỗi khi cắt đoạn {idx}: {str(e)}")

        else:
            # FAST/ACCURATE MODE: Xử lý tuần tự
            for idx, (start_time, end_time) in enumerate(segments, 1):
                duration = end_time - start_time
                segment_file = os.path.join(temp_dir, f"segment_{idx:03d}.mp4")
                segment_files.append(segment_file)

                log(f"✂️  Đoạn {idx}/{len(segments)}: "
                    f"{format_duration(start_time)} → {format_duration(end_time)} "
                    f"(Độ dài: {format_duration(duration)})")

                success = cut_single_segment(input_video, start_time, end_time, segment_file, mode)

                if not success:
                    raise RuntimeError(f"Lỗi khi cắt đoạn {idx}")

        cutting_time = time.time() - start_overall
        log(f"\n✅ Đã cắt xong {len(segments)} đoạn")
        log(f"⏱️  Tổng thời lượng video mới: {format_duration(total_duration)}")
        log(f"⚡ Thời gian cắt: {cutting_time:.1f}s\n")

        # Tạo file danh sách các đoạn để concatenate
        log("🔗 Đang ghép các đoạn lại với nhau...")
        concat_file = os.path.join(temp_dir, "concat_list.txt")
        with open(concat_file, 'w') as f:
            for segment_file in segment_files:
                # Sử dụng đường dẫn tuyệt đối
                abs_path = os.path.abspath(segment_file)
                f.write(f"file '{abs_path}'\n")

        # Ghép các đoạn lại
        concat_start = time.time()
        concat_cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            '-y',
            output_video
        ]

        result = subprocess.run(concat_cmd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

        if result.returncode != 0:
            raise RuntimeError(f"Lỗi khi ghép video: {result.stderr.decode()}")

        concat_time = time.time() - concat_start
        total_time = time.time() - start_overall

        log(f"✨ Hoàn thành! Video đã được lưu tại: {output_video}")
        log(f"📊 Thống kê:")
        log(f"   - Thời gian cắt: {cutting_time:.1f}s")
        log(f"   - Thời gian ghép: {concat_time:.1f}s")
        log(f"   - Tổng thời gian: {total_time:.1f}s")
        log(f"   - Tốc độ xử lý: {total_duration/total_time:.1f}x realtime\n")

    finally:
        # Dọn dẹp các file tạm (tùy chọn)
        if os.path.exists(temp_dir):
            import shutil
            try:
                shutil.rmtree(temp_dir)
                print("🧹 Đã xóa các file tạm")
            except Exception as e:
                print(f"⚠️  Không thể xóa thư mục tạm: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Công cụ cắt và ghép video - Video Cutter Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
  %(prog)s -i video.mp4 -s "03:05-03:10|40:05-40:10|1:03:05-1:04:05" -o output.mp4
  %(prog)s -i video.mp4 -s "segments" -o output.mp4 --mode fast
  %(prog)s -i video.mp4 -s "segments" -o output.mp4 --mode balanced --workers 4

Định dạng thời gian:
  MM:SS       - Ví dụ: 03:05 (3 phút 5 giây)
  HH:MM:SS    - Ví dụ: 1:03:05 (1 giờ 3 phút 5 giây)

Định dạng đoạn cắt:
  start1-end1|start2-end2|start3-end3
  Ví dụ: 03:05-03:10|40:05-40:10|1:03:05-1:04:05

Chế độ xử lý (--mode):
  fast      - 🚀 Rất nhanh (copy codec) - có thể sai lệch 1-2 giây
  balanced  - ⚡ Cân bằng (song song + re-encode) - nhanh và chính xác (MẶC ĐỊNH)
  accurate  - 🎯 Chính xác tuyệt đối (tuần tự + re-encode) - chậm nhất
        """
    )

    parser.add_argument('-i', '--input', required=True,
                       help='Đường dẫn video đầu vào')
    parser.add_argument('-s', '--segments', required=True,
                       help='Các đoạn cần cắt (format: start-end|start-end|...)')
    parser.add_argument('-o', '--output', required=True,
                       help='Đường dẫn video đầu ra')
    parser.add_argument('-t', '--temp-dir', default='temp_segments',
                       help='Thư mục tạm (mặc định: temp_segments)')
    parser.add_argument('-m', '--mode', default='balanced',
                       choices=['fast', 'balanced', 'accurate'],
                       help='Chế độ xử lý (mặc định: balanced)')
    parser.add_argument('-w', '--workers', type=int, default=None,
                       help='Số luồng song song cho balanced mode (mặc định: auto)')

    args = parser.parse_args()

    try:
        # Parse các đoạn cần cắt
        segments = parse_segments(args.segments)

        if not segments:
            print("❌ Không có đoạn nào để cắt!")
            sys.exit(1)

        # Thực hiện cắt video
        cut_video_segments(
            args.input,
            segments,
            args.output,
            temp_dir=args.temp_dir,
            mode=args.mode,
            max_workers=args.workers
        )

    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
