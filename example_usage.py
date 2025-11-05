#!/usr/bin/env python3
"""
Ví dụ sử dụng Video Cutter Tool
Demonstrating how to use the video cutter programmatically
"""

from video_cutter import parse_segments, cut_video_segments, parse_time_to_seconds


def example_1():
    """
    Ví dụ 1: Cắt 3 đoạn từ video dài 1 tiếng
    Kết quả: Video ngắn 1 phút 10 giây
    """
    print("=" * 60)
    print("VÍ DỤ 1: Cắt 3 đoạn từ video dài")
    print("=" * 60)

    input_video = "video_dai.mp4"  # Video đầu vào
    segments_str = "03:05-03:10|40:05-40:10|1:03:05-1:04:05"
    output_video = "video_ngan.mp4"

    # Parse segments
    segments = parse_segments(segments_str)

    print(f"Input: {input_video}")
    print(f"Segments: {segments_str}")
    print(f"Output: {output_video}")
    print(f"\nParsed segments: {segments}")

    # Tính tổng thời lượng
    total_duration = sum(end - start for start, end in segments)
    print(f"Total duration: {total_duration} seconds ({total_duration/60:.2f} minutes)")

    # Uncomment để chạy thực tế (cần có file video)
    # cut_video_segments(input_video, segments, output_video)


def example_2():
    """
    Ví dụ 2: Tạo video highlight từ webinar
    """
    print("\n" + "=" * 60)
    print("VÍ DỤ 2: Tạo video highlight")
    print("=" * 60)

    input_video = "webinar_full.mp4"
    segments_str = "00:30-01:00|15:20-16:45|45:00-47:30"
    output_video = "webinar_highlights.mp4"

    segments = parse_segments(segments_str)

    print(f"Input: {input_video}")
    print(f"Segments: {segments_str}")
    print(f"Output: {output_video}")
    print(f"\nSegment details:")

    for idx, (start, end) in enumerate(segments, 1):
        duration = end - start
        print(f"  Segment {idx}: {start}s - {end}s (duration: {duration}s)")

    total_duration = sum(end - start for start, end in segments)
    print(f"\nTotal duration: {total_duration} seconds ({total_duration/60:.2f} minutes)")


def example_3():
    """
    Ví dụ 3: Demo parse time function
    """
    print("\n" + "=" * 60)
    print("VÍ DỤ 3: Parse time formats")
    print("=" * 60)

    time_examples = [
        "00:30",      # 30 seconds
        "01:00",      # 1 minute
        "03:05",      # 3 minutes 5 seconds
        "15:20",      # 15 minutes 20 seconds
        "1:03:05",    # 1 hour 3 minutes 5 seconds
        "1:04:05",    # 1 hour 4 minutes 5 seconds
    ]

    for time_str in time_examples:
        seconds = parse_time_to_seconds(time_str)
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            formatted = f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            formatted = f"{minutes}m {secs}s"
        else:
            formatted = f"{secs}s"

        print(f"  {time_str:>10} = {seconds:>8.1f} seconds = {formatted}")


def example_4():
    """
    Ví dụ 4: Use case thực tế - Cắt quảng cáo từ video
    """
    print("\n" + "=" * 60)
    print("VÍ DỤ 4: Cắt bỏ quảng cáo (giữ lại nội dung chính)")
    print("=" * 60)

    # Giả sử video có quảng cáo tại:
    # - 05:00 - 05:30 (quảng cáo 1)
    # - 25:00 - 25:45 (quảng cáo 2)
    # - 50:00 - 50:30 (quảng cáo 3)

    # Ta sẽ cắt các phần KHÔNG phải quảng cáo
    input_video = "video_with_ads.mp4"
    segments_str = "00:00-05:00|05:30-25:00|25:45-50:00|50:30-60:00"
    output_video = "video_no_ads.mp4"

    segments = parse_segments(segments_str)

    print(f"Input: {input_video} (60 minutes với quảng cáo)")
    print(f"Output: {output_video} (không có quảng cáo)")
    print(f"\nContent segments (ads removed):")

    for idx, (start, end) in enumerate(segments, 1):
        duration = end - start
        print(f"  Part {idx}: {start/60:.2f}min - {end/60:.2f}min (duration: {duration/60:.2f}min)")

    total_duration = sum(end - start for start, end in segments)
    ads_removed = 3600 - total_duration  # 60 minutes - content
    print(f"\nOriginal: 60 minutes")
    print(f"Ads removed: {ads_removed/60:.2f} minutes")
    print(f"Final video: {total_duration/60:.2f} minutes")


if __name__ == '__main__':
    print("\n🎬 VIDEO CUTTER TOOL - EXAMPLES")
    print("=" * 60)

    example_1()
    example_2()
    example_3()
    example_4()

    print("\n" + "=" * 60)
    print("💡 TIP: Để chạy thực tế, uncomment dòng cut_video_segments()")
    print("    và đảm bảo bạn có file video đầu vào")
    print("=" * 60)
