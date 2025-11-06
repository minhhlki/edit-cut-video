#!/usr/bin/env python3
"""
Rclone Uploader
Upload files to Google Drive using rclone
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path


class RcloneUploader:
    """Upload files using rclone"""

    def __init__(self, rclone_config_content):
        """
        Initialize uploader with rclone config content

        Args:
            rclone_config_content: Content of rclone.conf as string
        """
        self.config_content = rclone_config_content
        self.config_file = None
        self._setup_config()

    def _setup_config(self):
        """Setup rclone config file"""
        # Create temp config file
        self.config_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.conf',
            delete=False
        )
        self.config_file.write(self.config_content)
        self.config_file.close()

        print(f"✅ Rclone config created: {self.config_file.name}")

    def check_rclone_installed(self):
        """Check if rclone is installed"""
        try:
            result = subprocess.run(
                ['rclone', 'version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def list_remotes(self):
        """List available remotes in config"""
        try:
            result = subprocess.run(
                ['rclone', 'listremotes', '--config', self.config_file.name],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                remotes = [line.strip().rstrip(':') for line in result.stdout.strip().split('\n') if line.strip()]
                return remotes
            else:
                print(f"❌ Error listing remotes: {result.stderr}")
                return []
        except Exception as e:
            print(f"❌ Error: {e}")
            return []

    def upload_file(self, file_path, remote_name='gdrive', remote_path='', progress_callback=None):
        """
        Upload a file using rclone

        Args:
            file_path: Path to the file to upload
            remote_name: Name of the remote (default: gdrive)
            remote_path: Path on remote (default: root)
            progress_callback: Callback function for progress updates

        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False

        if not self.check_rclone_installed():
            print("❌ rclone is not installed!")
            print("Install with: sudo apt-get install rclone")
            return False

        file_name = Path(file_path).name
        print(f"📤 Uploading: {file_name}")
        print(f"📁 Remote: {remote_name}:{remote_path}")

        # Build rclone copy command
        destination = f"{remote_name}:{remote_path}"

        cmd = [
            'rclone',
            'copy',
            file_path,
            destination,
            '--config', self.config_file.name,
            '--progress',
            '--stats', '1s',
            '--stats-one-line'
        ]

        try:
            # Run rclone with real-time progress
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # Read output line by line
            for line in process.stdout:
                line = line.strip()
                if line:
                    # Print progress
                    print(f'\r{line}', end='', flush=True)

                    if progress_callback:
                        progress_callback(line)

            process.wait()
            print()  # New line after progress

            if process.returncode == 0:
                print(f"✅ Upload complete!")
                return True
            else:
                print(f"❌ Upload failed with return code: {process.returncode}")
                return False

        except Exception as e:
            print(f"\n❌ Upload error: {e}")
            return False

    def cleanup(self):
        """Clean up temporary config file"""
        if self.config_file and os.path.exists(self.config_file.name):
            try:
                os.unlink(self.config_file.name)
                print(f"🗑️  Cleaned up config file")
            except Exception as e:
                print(f"⚠️  Could not delete temp config: {e}")

    def __del__(self):
        """Destructor to clean up"""
        self.cleanup()


def main():
    """Main function for testing"""
    if len(sys.argv) < 2:
        print("Usage: python rclone_uploader.py <file_to_upload> [rclone.conf]")
        sys.exit(1)

    file_path = sys.argv[1]
    config_path = sys.argv[2] if len(sys.argv) > 2 else "rclone.conf"

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        print("\nPlease provide an rclone.conf file")
        sys.exit(1)

    # Load config
    with open(config_path, 'r') as f:
        config_content = f.read()

    # Upload file
    uploader = RcloneUploader(config_content)

    # List available remotes
    remotes = uploader.list_remotes()
    if remotes:
        print(f"📋 Available remotes: {', '.join(remotes)}")
        remote_name = remotes[0]
    else:
        print("⚠️  No remotes found, using 'gdrive' as default")
        remote_name = 'gdrive'

    # Upload
    remote_path = input(f"Enter remote path (default: root): ").strip()

    success = uploader.upload_file(file_path, remote_name, remote_path)

    if success:
        print(f"\n✅ Success!")
    else:
        print("\n❌ Upload failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
