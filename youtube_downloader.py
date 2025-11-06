#!/usr/bin/env python3
"""
YouTube Video Downloader
Downloads YouTube videos in the highest available resolution.
"""

import os
import sys
import argparse
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print("Error: yt-dlp is not installed.")
    print("Please install it using: pip install yt-dlp")
    sys.exit(1)


class YouTubeDownloader:
    """YouTube video downloader with highest resolution support."""

    def __init__(self, output_path="downloads"):
        """
        Initialize the downloader.

        Args:
            output_path (str): Directory where videos will be saved
        """
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)

    def download_video(self, url, output_filename=None, progress_callback=None):
        """
        Download a YouTube video in the highest available resolution.

        Args:
            url (str): YouTube video URL
            output_filename (str, optional): Custom output filename
            progress_callback (callable, optional): Callback for progress updates

        Returns:
            tuple: (success: bool, file_path: str or None)
        """
        try:
            # Store callback for use in hook
            self.progress_callback = progress_callback

            # Configure yt-dlp options for highest quality
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': str(self.output_path / (output_filename or '%(title)s.%(ext)s')),
                'merge_output_format': 'mp4',
                'progress_hooks': [self._progress_hook],
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            }

            # Download the video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"\n📥 Fetching video information...")
                if progress_callback:
                    progress_callback("📥 Đang lấy thông tin video...")

                info = ydl.extract_info(url, download=False)

                # Display video information
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                uploader = info.get('uploader', 'Unknown')

                print(f"\n📹 Video: {title}")
                print(f"⏱️  Duration: {self._format_duration(duration)}")
                print(f"👤 Channel: {uploader}")

                if progress_callback:
                    progress_callback(f"📹 Video: {title}")
                    progress_callback(f"⏱️  Thời lượng: {self._format_duration(duration)}")

                # Get available formats
                formats = info.get('formats', [])
                if formats:
                    max_height = max([f.get('height', 0) for f in formats if f.get('height')])
                    print(f"🎬 Maximum resolution: {max_height}p")
                    if progress_callback:
                        progress_callback(f"🎬 Độ phân giải: {max_height}p")

                print(f"\n⬇️  Downloading to: {self.output_path}")
                print("=" * 50)

                if progress_callback:
                    progress_callback("⬇️  Bắt đầu tải xuống...")

                # Download the video
                ydl.download([url])

                # Get the actual downloaded file path
                downloaded_file = ydl.prepare_filename(info)

                print("\n✅ Download completed successfully!")
                if progress_callback:
                    progress_callback("✅ Tải xuống hoàn tất!")

                return True, downloaded_file

        except yt_dlp.utils.DownloadError as e:
            error_msg = f"Download error: {e}"
            print(f"\n❌ {error_msg}")
            if progress_callback:
                progress_callback(f"❌ Lỗi: {error_msg}")
            return False, None
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            print(f"\n❌ {error_msg}")
            if progress_callback:
                progress_callback(f"❌ Lỗi: {error_msg}")
            return False, None

    def get_video_info(self, url):
        """
        Get information about a YouTube video without downloading.

        Args:
            url (str): YouTube video URL

        Returns:
            dict: Video information or None if error
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'views': info.get('view_count', 0),
                    'formats': len(info.get('formats', [])),
                }
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None

    def _progress_hook(self, d):
        """Hook to display download progress."""
        if d['status'] == 'downloading':
            # Calculate progress
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)

            if total > 0:
                percent = (downloaded / total) * 100
                downloaded_mb = downloaded / (1024 * 1024)
                total_mb = total / (1024 * 1024)
                speed = d.get('speed', 0)
                speed_mb = speed / (1024 * 1024) if speed else 0

                # Print progress bar
                bar_length = 30
                filled = int(bar_length * downloaded / total)
                bar = '█' * filled + '░' * (bar_length - filled)

                msg = f'{bar} {percent:.1f}% | {downloaded_mb:.1f}/{total_mb:.1f} MB | {speed_mb:.2f} MB/s'
                print(f'\r{msg}', end='')

                if self.progress_callback:
                    self.progress_callback(f'⬇️  {percent:.1f}% | {downloaded_mb:.1f}/{total_mb:.1f} MB')

        elif d['status'] == 'finished':
            print('\n\n🔄 Processing video...')
            if self.progress_callback:
                self.progress_callback('🔄 Đang xử lý video...')

    @staticmethod
    def _format_duration(seconds):
        """Format duration in seconds to readable format."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"


def main():
    """Main function to run the downloader from command line."""
    parser = argparse.ArgumentParser(
        description='Download YouTube videos in the highest available resolution',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://www.youtube.com/watch?v=dQw4w9WgXcQ
  %(prog)s https://youtu.be/dQw4w9WgXcQ -o my_video.mp4
  %(prog)s https://www.youtube.com/watch?v=dQw4w9WgXcQ -d ./my_videos
  %(prog)s https://www.youtube.com/watch?v=dQw4w9WgXcQ --info
        """
    )

    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument('-o', '--output', help='Output filename (default: video title)')
    parser.add_argument('-d', '--directory', default='downloads',
                        help='Output directory (default: downloads)')
    parser.add_argument('--info', action='store_true',
                        help='Show video information without downloading')

    args = parser.parse_args()

    # Create downloader instance
    downloader = YouTubeDownloader(output_path=args.directory)

    # Show info only or download
    if args.info:
        print("Fetching video information...")
        info = downloader.get_video_info(args.url)
        if info:
            print(f"\n📹 Title: {info['title']}")
            print(f"⏱️  Duration: {YouTubeDownloader._format_duration(info['duration'])}")
            print(f"👤 Uploader: {info['uploader']}")
            print(f"👁️  Views: {info['views']:,}")
            print(f"🎬 Available formats: {info['formats']}")
    else:
        # Download the video
        success, file_path = downloader.download_video(args.url, args.output)
        if success and file_path:
            print(f"\n📁 Saved to: {file_path}")


if __name__ == "__main__":
    main()
