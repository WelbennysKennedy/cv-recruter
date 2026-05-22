import json
import uuid
from pathlib import Path

import googleapiclient
import gspread
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPE = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
GOOGLE_CREDENTIALS_FILE = Path('credentials.json')
GOOGLE_TOKEN_FILE = Path('token.json')


def _load_google_credentials():
    config = json.loads(GOOGLE_CREDENTIALS_FILE.read_text(encoding='utf-8'))

    if config.get('type') == 'service_account':
        return service_account.Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_FILE,
            scopes=SCOPE,
        )

    if 'installed' in config or 'web' in config:
        credentials = None
        if GOOGLE_TOKEN_FILE.exists():
            credentials = Credentials.from_authorized_user_file(GOOGLE_TOKEN_FILE, SCOPE)

        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

        if not credentials or not credentials.valid:
            flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CREDENTIALS_FILE, SCOPE)
            credentials = flow.run_local_server(port=0)

        GOOGLE_TOKEN_FILE.write_text(credentials.to_json(), encoding='utf-8')
        return credentials

    raise ValueError(
        'credentials.json deve ser uma credencial OAuth instalada ou uma service account.'
    )


CREDENTIALS = _load_google_credentials()
CLIENT_SHEETS = gspread.authorize(CREDENTIALS)
CLIENT_DRIVE = build('drive', 'v3', credentials=CREDENTIALS)


class AccessResume:
    def __init__(self, sheets_name) -> None:
        self.sheet = CLIENT_SHEETS.open(sheets_name).sheet1

    def _get_all_values_in_sheet(self):
        return self.sheet.get_all_values()

    def get_resumes_id(self):
        return [line[-2].split('id=')[-1] for line in self._get_all_values_in_sheet()]
    
    def get_resumes_ids_unprocessed(self, know_id):
        ids = self.get_resumes_id()
        index = ids.index(know_id)
        return ids[index + 1:]

    def download_file(self, file_id):
        request = CLIENT_DRIVE.files().get_media(fileId=file_id)
        full_path = f'storage/{str(uuid.uuid4())}'
        with open(full_path, "wb") as file:
            downloader = googleapiclient.http.MediaIoBaseDownload(file, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
        
        return full_path

    def check_file_access(file_id):
        try:
            CLIENT_DRIVE.files().get(fileId=file_id).execute()
        except googleapiclient.errors.HttpError as error:
            if error.resp.status == 404:
                raise Exception("File not found. Check the file ID or permissions.")
            else:
                raise Exception("Another error occurred.")
