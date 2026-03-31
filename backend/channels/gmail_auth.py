"""
Gmail OAuth2 Authentication.
Run this ONCE to generate token.json
"""
import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]

CREDENTIALS_FILE = "../context/credentials.json"
TOKEN_FILE = "../context/token.json"

def get_gmail_service():
    """Get authenticated Gmail service."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

if __name__ == "__main__":
    print("Starting Gmail OAuth flow...")
    service = get_gmail_service()
    profile = service.users().getProfile(userId='me').execute()
    print(f"✅ Authenticated as: {profile['emailAddress']}")
    print(f"✅ Token saved to: {TOKEN_FILE}")
