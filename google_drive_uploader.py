#!/usr/bin/env python3
"""
Google Drive Uploader
Upload files to Google Drive using service account credentials
"""

import os
import sys
import io
from pathlib import Path

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
    from google.oauth2 import service_account
    GDRIVE_AVAILABLE = True
except ImportError:
    GDRIVE_AVAILABLE = False
    print("Warning: Google Drive API not available")
    print("Install with: pip install google-api-python-client google-auth")


class GoogleDriveUploader:
    """Upload files to Google Drive using service account"""

    def __init__(self, credentials_dict):
        """
        Initialize uploader with service account credentials

        Args:
            credentials_dict: Dictionary containing service account credentials
        """
        if not GDRIVE_AVAILABLE:
            raise ImportError("Google Drive API libraries not installed")

        self.credentials = service_account.Credentials.from_service_account_info(
            credentials_dict,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )

        self.service = build('drive', 'v3', credentials=self.credentials)

    def get_or_create_folder(self, folder_name):
        """
        Get folder ID or create if doesn't exist

        Args:
            folder_name: Name of the folder

        Returns:
            Folder ID
        """
        # Search for folder
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"

        try:
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()

            folders = results.get('files', [])

            if folders:
                print(f"📁 Found existing folder: {folder_name}")
                return folders[0]['id']

            # Create folder if not found
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }

            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()

            print(f"📁 Created new folder: {folder_name}")
            return folder.get('id')

        except Exception as e:
            print(f"❌ Error with folder: {e}")
            return None

    def upload_file(self, file_path, file_name=None, folder_name=None, progress_callback=None):
        """
        Upload a file to Google Drive

        Args:
            file_path: Path to the file to upload
            file_name: Name for the file on Drive (default: original filename)
            folder_name: Name of folder to upload to (optional)
            progress_callback: Callback function for progress updates

        Returns:
            File ID if successful, None otherwise
        """
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return None

        if not file_name:
            file_name = Path(file_path).name

        print(f"📤 Uploading: {file_name}")

        # Get or create folder
        parent_id = None
        if folder_name:
            parent_id = self.get_or_create_folder(folder_name)

        # File metadata
        file_metadata = {'name': file_name}

        if parent_id:
            file_metadata['parents'] = [parent_id]

        # Media upload
        media = MediaFileUpload(
            file_path,
            resumable=True
        )

        try:
            # Create the file
            request = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            )

            response = None
            file_size = os.path.getsize(file_path)
            uploaded = 0

            while response is None:
                status, response = request.next_chunk()

                if status:
                    uploaded = int(status.resumable_progress)
                    percent = (uploaded / file_size) * 100

                    # Progress bar
                    bar_length = 30
                    filled = int(bar_length * uploaded / file_size)
                    bar = '█' * filled + '░' * (bar_length - filled)

                    mb_uploaded = uploaded / (1024 * 1024)
                    mb_total = file_size / (1024 * 1024)

                    print(f'\r{bar} {percent:.1f}% | {mb_uploaded:.1f}/{mb_total:.1f} MB', end='', flush=True)

                    if progress_callback:
                        progress_callback(percent, uploaded, file_size)

            print()  # New line after progress bar

            file_id = response.get('id')
            web_link = response.get('webViewLink')

            print(f"✅ Upload complete!")
            print(f"📄 File ID: {file_id}")

            if web_link:
                print(f"🔗 Link: {web_link}")

            return file_id

        except Exception as e:
            print(f"\n❌ Upload failed: {e}")
            return None

    def get_file_link(self, file_id):
        """
        Get shareable link for a file

        Args:
            file_id: ID of the file

        Returns:
            Shareable link or None
        """
        try:
            # Make file publicly accessible (optional)
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }

            self.service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()

            # Get file metadata
            file = self.service.files().get(
                fileId=file_id,
                fields='webViewLink, webContentLink'
            ).execute()

            return file.get('webViewLink')

        except Exception as e:
            print(f"⚠️  Could not get shareable link: {e}")
            return None

    def list_files(self, folder_name=None, max_results=10):
        """
        List files in Google Drive

        Args:
            folder_name: Name of folder to list (optional)
            max_results: Maximum number of results

        Returns:
            List of files
        """
        try:
            query = "trashed=false"

            if folder_name:
                folder_id = self.get_or_create_folder(folder_name)
                if folder_id:
                    query += f" and '{folder_id}' in parents"

            results = self.service.files().list(
                q=query,
                pageSize=max_results,
                fields='files(id, name, mimeType, createdTime, size)',
                orderBy='createdTime desc'
            ).execute()

            files = results.get('files', [])

            if not files:
                print('📭 No files found')
                return []

            print(f'\n📁 Files ({len(files)}):')
            for file in files:
                size_mb = int(file.get('size', 0)) / (1024 * 1024) if file.get('size') else 0
                print(f"  • {file['name']} ({size_mb:.2f} MB) - ID: {file['id']}")

            return files

        except Exception as e:
            print(f"❌ Error listing files: {e}")
            return []


def main():
    """Main function for testing"""
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python google_drive_uploader.py <file_to_upload> [credentials.json]")
        sys.exit(1)

    file_path = sys.argv[1]
    creds_path = sys.argv[2] if len(sys.argv) > 2 else "credentials.json"

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    if not os.path.exists(creds_path):
        print(f"❌ Credentials file not found: {creds_path}")
        print("\nPlease provide a service account JSON file")
        sys.exit(1)

    # Load credentials
    with open(creds_path, 'r') as f:
        credentials = json.load(f)

    # Upload file
    uploader = GoogleDriveUploader(credentials)

    file_name = Path(file_path).name
    folder_name = "Video Cutter Uploads"

    file_id = uploader.upload_file(file_path, file_name, folder_name)

    if file_id:
        print(f"\n✅ Success! File ID: {file_id}")

        # Get shareable link
        link = uploader.get_file_link(file_id)
        if link:
            print(f"🔗 Shareable link: {link}")
    else:
        print("\n❌ Upload failed")
        sys.exit(1)


if __name__ == "__main__":
    if not GDRIVE_AVAILABLE:
        print("❌ Google Drive API not available")
        print("Install with: pip install google-api-python-client google-auth")
        sys.exit(1)

    main()
