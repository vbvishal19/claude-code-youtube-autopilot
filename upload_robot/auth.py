"""OAuth for the upload robot. Keys live in files, never in chat or code.

YT_CLIENT_FILE  path to your OAuth client JSON (Desktop app type)
YT_TOKEN_FILE   where the refreshable token is stored (one file per channel)
"""
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]


def credentials():
    client = os.environ.get("YT_CLIENT_FILE", "secrets/youtube-client.json")
    token = Path(os.environ.get("YT_TOKEN_FILE", "secrets/youtube-token.json"))
    creds = Credentials.from_authorized_user_file(str(token), SCOPES) if token.exists() else None
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    elif not creds or not creds.valid:
        # Opens a browser. Sign in with the account that owns the target channel,
        # then pick that channel. upload.py still verifies it before every upload.
        creds = InstalledAppFlow.from_client_secrets_file(client, SCOPES).run_local_server(port=0)
    token.parent.mkdir(parents=True, exist_ok=True)
    token.write_text(creds.to_json(), encoding="utf-8")
    return creds
