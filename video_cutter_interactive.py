#!/usr/bin/env python3
"""
Video Cutter Tool - Interactive CLI
Interactive command-line interface for video cutting with all features
"""

import os
import sys
import json
from pathlib import Path

# Import our modules
try:
    from video_cutter import cut_video_segments, parse_segments, check_ffmpeg
    from youtube_downloader import YouTubeDownloader
    YOUTUBE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some modules not available: {e}")
    YOUTUBE_AVAILABLE = False

# Import Rclone uploader
try:
    from rclone_uploader import RcloneUploader
    RCLONE_AVAILABLE = True
except ImportError:
    RCLONE_AVAILABLE = False


def print_header():
    """Print welcome header"""
    print("\n" + "=" * 60)
    print("🎬 VIDEO CUTTER TOOL - Interactive Mode")
    print("=" * 60 + "\n")


def print_separator():
    """Print separator line"""
    print("-" * 60)


def get_input(prompt, default=None, optional=False):
    """Get user input with optional default value"""
    if default:
        prompt = f"{prompt} [{default}]"
    if optional:
        prompt = f"{prompt} (Optional, press Enter to skip)"

    prompt += ": "
    value = input(prompt).strip()

    if not value and default:
        return default
    if not value and optional:
        return None

    return value


def get_choice(prompt, options, default=None):
    """Get user choice from options"""
    print(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        marker = " (default)" if default and i == default else ""
        print(f"  {i}. {option}{marker}")

    while True:
        choice = input(f"\nYour choice [1-{len(options)}]: ").strip()

        if not choice and default:
            return default

        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(options):
                return choice_num
            else:
                print(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("Please enter a valid number")


def get_yes_no(prompt, default=False):
    """Get yes/no input"""
    default_str = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_str}]: ").strip().lower()

    if not response:
        return default

    return response in ['y', 'yes', '1', 'true']


def download_youtube_video(url):
    """Download video from YouTube"""
    if not YOUTUBE_AVAILABLE:
        print("❌ YouTube downloader not available. Please check yt-dlp installation.")
        return None

    print("\n📥 Downloading video from YouTube...")
    print_separator()

    downloader = YouTubeDownloader(output_path="downloads")

    def progress_callback(message):
        print(f"\r{message}", end='', flush=True)

    success, file_path = downloader.download_video(url, progress_callback=progress_callback)

    if success:
        print(f"\n✅ Downloaded successfully: {file_path}")
        return file_path
    else:
        print("\n❌ Download failed")
        return None


def validate_segments(segments_str):
    """Validate segment format"""
    try:
        segments = parse_segments(segments_str)
        print(f"\n✅ Valid format! Found {len(segments)} segments:")

        total_duration = 0
        for idx, (start, end) in enumerate(segments, 1):
            duration = end - start
            total_duration += duration
            print(f"  Segment {idx}: {start}s - {end}s ({duration}s)")

        print(f"\nTotal output duration: {total_duration}s ({total_duration/60:.2f} minutes)")
        return True
    except Exception as e:
        print(f"\n❌ Invalid format: {e}")
        print("\nExpected format: MM:SS-MM:SS|MM:SS-MM:SS")
        print("Example: 03:05-03:10|40:05-40:10|1:03:05-1:04:05")
        return False


def get_rclone_config():
    """Get rclone config content"""
    if not RCLONE_AVAILABLE:
        print("⚠️  Rclone uploader not available.")
        return None

    print("\n📤 Rclone Configuration")
    print_separator()
    print("Please paste your rclone.conf content.")
    print("Example format:")
    print("  [gdrive]")
    print("  type = drive")
    print("  scope = drive")
    print("  token = {...}")
    print("  team_drive = ")
    print()
    print("(Paste the entire config, then press Enter twice)")
    print()

    config_lines = []
    print("Paste rclone.conf (press Enter twice when done):")

    empty_count = 0
    while empty_count < 2:
        line = input()
        if not line.strip():
            empty_count += 1
        else:
            empty_count = 0
            config_lines.append(line)

    config_str = '\n'.join(config_lines)

    if not config_str.strip():
        return None

    # Basic validation - check if it looks like rclone config
    if '[' not in config_str or 'type' not in config_str:
        print("⚠️  Config doesn't look like a valid rclone config")
        print("Expected format with [remote_name] and type = ...")
        return None

    print("✅ Valid rclone config!")
    return config_str


def upload_with_rclone(file_path, rclone_config, remote_path=''):
    """Upload file using rclone"""
    if not RCLONE_AVAILABLE:
        print("❌ Rclone uploader not available")
        return False

    print("\n📤 Uploading with rclone...")
    print_separator()

    try:
        uploader = RcloneUploader(rclone_config)

        # List available remotes
        remotes = uploader.list_remotes()
        if remotes:
            print(f"📋 Available remotes: {', '.join(remotes)}")
            remote_name = remotes[0]
            print(f"🎯 Using remote: {remote_name}")
        else:
            print("⚠️  No remotes found in config")
            return False

        # Upload
        success = uploader.upload_file(file_path, remote_name, remote_path)

        if success:
            print(f"\n✅ Uploaded successfully!")
            return True
        else:
            print("\n❌ Upload failed")
            return False
    except Exception as e:
        print(f"\n❌ Upload error: {e}")
        return False


def main():
    """Main interactive function"""
    print_header()

    # Check ffmpeg
    if not check_ffmpeg():
        print("❌ ffmpeg not found! Please install it first:")
        print("   sudo apt-get install ffmpeg")
        sys.exit(1)

    print("✅ ffmpeg is installed")
    print()

    # Step 1: YouTube Download (Optional)
    print_separator()
    print("STEP 1: Video Source")
    print_separator()

    youtube_url = get_input("🔗 YouTube URL", optional=True)
    input_video = None

    if youtube_url:
        input_video = download_youtube_video(youtube_url)
        if not input_video:
            print("⚠️  Download failed. Please provide a local video file instead.")

    # Step 2: Input Video
    if not input_video:
        print()
        while True:
            input_video = get_input("📹 Input video path")
            if os.path.exists(input_video):
                print(f"✅ Found: {input_video}")
                break
            else:
                print(f"❌ File not found: {input_video}")

    # Step 3: Segments
    print()
    print_separator()
    print("STEP 2: Segments to Cut")
    print_separator()
    print("Format: MM:SS-MM:SS|MM:SS-MM:SS|...")
    print("Example: 03:05-03:10|40:05-40:10|1:03:05-1:04:05")
    print()

    while True:
        segments_str = get_input("✂️  Segments")
        if validate_segments(segments_str):
            break

    segments = parse_segments(segments_str)

    # Step 4: Output Video
    print()
    print_separator()
    print("STEP 3: Output Configuration")
    print_separator()

    default_output = str(Path(input_video).stem) + "_cut" + Path(input_video).suffix
    output_video = get_input("💾 Output video path", default=default_output)

    # Step 5: Processing Mode
    print()
    modes = [
        "🚀 Fast - Rất nhanh (10-20x, có thể sai lệch ±1-2s)",
        "⚡ Balanced - Cân bằng (3-4x, chính xác 100%)",
        "🎯 Accurate - Chính xác tuyệt đối (chậm nhất)"
    ]
    mode_map = {1: 'fast', 2: 'balanced', 3: 'accurate'}

    mode_choice = get_choice("⚙️  Processing mode", modes, default=2)
    mode = mode_map[mode_choice]

    # Step 6: Audio Option
    print()
    remove_audio = get_yes_no("🔊 Remove audio (create silent video)?", default=False)

    # Step 7: Rclone Upload (Optional)
    print()
    print_separator()
    print("STEP 4: Rclone Upload (Optional)")
    print_separator()

    rclone_config = None
    remote_path = ''
    upload_enabled = get_yes_no("📤 Upload with rclone after processing?", default=False)

    if upload_enabled:
        rclone_config = get_rclone_config()
        if not rclone_config:
            print("⚠️  No valid rclone config provided. Skipping upload.")
            upload_enabled = False
        else:
            # Ask for remote path (optional)
            print()
            remote_path = get_input(
                "📁 Remote path (folder in Google Drive)",
                default="",
                optional=True
            ) or ''

    # Summary
    print()
    print_separator()
    print("📋 SUMMARY")
    print_separator()
    print(f"Input: {input_video}")
    print(f"Segments: {len(segments)} segments")
    print(f"Output: {output_video}")
    print(f"Mode: {mode.upper()}")
    print(f"Audio: {'OFF (Silent)' if remove_audio else 'ON'}")
    print(f"Rclone Upload: {'YES' if upload_enabled else 'NO'}")
    if upload_enabled and remote_path:
        print(f"Remote Path: {remote_path}")
    print_separator()
    print()

    if not get_yes_no("▶️  Start processing?", default=True):
        print("❌ Cancelled by user")
        return

    # Process video
    print()
    print("=" * 60)
    print("🎬 PROCESSING VIDEO")
    print("=" * 60)
    print()

    try:
        cut_video_segments(
            input_video=input_video,
            segments=segments,
            output_video=output_video,
            mode=mode,
            remove_audio=remove_audio
        )

        print()
        print("=" * 60)
        print("✅ VIDEO PROCESSING COMPLETE!")
        print("=" * 60)
        print(f"\n📁 Output saved to: {output_video}")

        # Upload with rclone if requested
        if upload_enabled and rclone_config:
            print()
            if upload_with_rclone(output_video, rclone_config, remote_path):
                print("\n✅ Upload complete!")
            else:
                print("\n⚠️  Upload failed")

        print()
        print("🎉 All done! Thank you for using Video Cutter Tool!")
        print()

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERROR")
        print("=" * 60)
        print(f"\n{e}")
        print()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
