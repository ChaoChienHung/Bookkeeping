"""
Google Drive Integration Service
"""
import io
import os
import pandas as pd
from typing import Optional
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from app.config import settings


class GoogleDriveService:
    """Handles Google Drive operations"""
    
    def __init__(self):
        self.credentials = None
        self.service = None
        self.folder_id = settings.DRIVE_FOLDER_ID
        self.scopes = settings.GOOGLE_SCOPES
    
    def authenticate(self) -> bool:
        """Authenticate with Google Drive"""
        creds = None
        
        # Load existing credentials
        if os.path.exists(settings.GOOGLE_TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(
                settings.GOOGLE_TOKEN_FILE,
                self.scopes
            )
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(settings.GOOGLE_CREDENTIALS_FILE):
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.GOOGLE_CREDENTIALS_FILE,
                    self.scopes
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(settings.GOOGLE_TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        
        self.credentials = creds
        self.service = build('drive', 'v3', credentials=creds)
        return True
    
    def upload_csv(
        self,
        file_path: str,
        file_name: str = None,
        convert_to_sheets: bool = True
    ) -> dict:
        """Upload CSV file to Google Drive"""
        if not self.service:
            if not self.authenticate():
                return {
                    "success": False,
                    "error": "Authentication failed"
                }
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        if file_name is None:
            file_name = os.path.basename(file_path)
        
        file_metadata = {
            'name': file_name,
            'parents': [self.folder_id]
        }
        
        if convert_to_sheets:
            file_metadata['mimeType'] = 'application/vnd.google-apps.spreadsheet'
        
        media = MediaFileUpload(file_path, mimetype='text/csv')
        
        try:
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()
            
            return {
                "success": True,
                "file_id": file.get('id'),
                "file_name": file.get('name'),
                "web_link": file.get('webViewLink')
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def download_csv(self, file_id: str) -> Optional[pd.DataFrame]:
        """Download CSV/Spreadsheet from Google Drive"""
        if not self.service:
            if not self.authenticate():
                return None
        
        try:
            request = self.service.files().export_media(
                fileId=file_id,
                mimeType='text/csv'
            )
            
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            fh.seek(0)
            df = pd.read_csv(fh, parse_dates=['Date'])
            return df
            
        except Exception as e:
            print(f"Error downloading file: {e}")
            return None
    
    def list_files(self, folder_id: str = None, page_size: int = 10) -> dict:
        """List files in Google Drive folder"""
        if not self.service:
            if not self.authenticate():
                return {
                    "success": False,
                    "error": "Authentication failed"
                }
        
        if folder_id is None:
            folder_id = self.folder_id
        
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                pageSize=page_size,
                fields="files(id, name, mimeType, createdTime, modifiedTime, webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            
            return {
                "success": True,
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_file(self, file_id: str) -> dict:
        """Delete a file from Google Drive"""
        if not self.service:
            if not self.authenticate():
                return {
                    "success": False,
                    "error": "Authentication failed"
                }
        
        try:
            self.service.files().delete(fileId=file_id).execute()
            return {
                "success": True,
                "message": f"File {file_id} deleted successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
