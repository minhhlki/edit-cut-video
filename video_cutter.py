#!/usr/bin/env python3
"""
Video Cutter Tool - Công cụ cắt và ghép video
Cho phép cắt nhiều đoạn từ video dài và ghép chúng lại với nhau
"""

import os
import sys
import subprocess
import argparse
from typing import List, Tuple
import re


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


def cut_video_segments(input_video: str, segments: List[Tuple[float, float]],
                       output_video: str, temp_dir: str = "temp_segments"):
    """
    Cắt và ghép các đoạn video

    Args:
        input_video: Đường dẫn video đầu vào
        segments: List các tuple (start_time, end_time)
        output_video: Đường dẫn video đầu ra
        temp_dir: Thư mục tạm để lưu các đoạn video
    """
    # Kiểm tra ffmpeg
    if not check_ffmpeg():
        raise RuntimeError("ffmpeg chưa được cài đặt. Vui lòng cài đặt ffmpeg trước.")

    # Kiểm tra file đầu vào
    if not os.path.exists(input_video):
        raise FileNotFoundError(f"Không tìm thấy file video: {input_video}")

    # Tạo thư mục tạm
    os.makedirs(temp_dir, exist_ok=True)

    segment_files = []
    total_duration = 0

    print(f"\n🎬 Bắt đầu cắt video từ: {input_video}")
    print(f"📊 Tổng số đoạn cần cắt: {len(segments)}\n")

    try:
        # Cắt từng đoạn
        for idx, (start_time, end_time) in enumerate(segments, 1):
            duration = end_time - start_time
            total_duration += duration

            segment_file = os.path.join(temp_dir, f"segment_{idx:03d}.mp4")
            segment_files.append(segment_file)

            print(f"✂️  Đoạn {idx}/{len(segments)}: "
                  f"{format_duration(start_time)} → {format_duration(end_time)} "
                  f"(Độ dài: {format_duration(duration)})")

            # Sử dụng ffmpeg để cắt đoạn video
            # -ss: thời gian bắt đầu
            # -t: độ dài đoạn cần cắt
            # -c copy: copy codec (nhanh hơn nhưng có thể không chính xác)
            # Hoặc dùng -c:v libx264 -c:a aac để encode lại (chậm hơn nhưng chính xác)
            cmd = [
                'ffmpeg',
                '-ss', str(start_time),
                '-i', input_video,
                '-t', str(duration),
                '-c:v', 'libx264',  # Encode lại để đảm bảo chính xác
                '-c:a', 'aac',
                '-strict', 'experimental',
                '-y',  # Ghi đè file nếu tồn tại
                segment_file
            ]

            result = subprocess.run(cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

            if result.returncode != 0:
                raise RuntimeError(f"Lỗi khi cắt đoạn {idx}: {result.stderr.decode()}")

        print(f"\n✅ Đã cắt xong {len(segments)} đoạn")
        print(f"⏱️  Tổng thời lượng video mới: {format_duration(total_duration)}\n")

        # Tạo file danh sách các đoạn để concatenate
        concat_file = os.path.join(temp_dir, "concat_list.txt")
        with open(concat_file, 'w') as f:
            for segment_file in segment_files:
                # Sử dụng đường dẫn tuyệt đối
                abs_path = os.path.abspath(segment_file)
                f.write(f"file '{abs_path}'\n")

        print("🔗 Đang ghép các đoạn lại với nhau...")

        # Ghép các đoạn lại
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

        print(f"✨ Hoàn thành! Video đã được lưu tại: {output_video}\n")

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
  %(prog)s -i long_video.mp4 -s "00:30-01:00|05:00-05:30" -o highlights.mp4

Định dạng thời gian:
  MM:SS       - Ví dụ: 03:05 (3 phút 5 giây)
  HH:MM:SS    - Ví dụ: 1:03:05 (1 giờ 3 phút 5 giây)

Định dạng đoạn cắt:
  start1-end1|start2-end2|start3-end3
  Ví dụ: 03:05-03:10|40:05-40:10|1:03:05-1:04:05
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

    args = parser.parse_args()

    try:
        # Parse các đoạn cần cắt
        segments = parse_segments(args.segments)

        if not segments:
            print("❌ Không có đoạn nào để cắt!")
            sys.exit(1)

        # Thực hiện cắt video
        cut_video_segments(args.input, segments, args.output, args.temp_dir)

    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
