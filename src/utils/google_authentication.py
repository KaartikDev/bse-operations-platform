import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
from google.cloud import secretmanager

# Replace with your actual project ID
PROJECT_ID = "your-project-id"
SECRET_ID = "google_sheets_token"

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/gmail.send"] # will need to move this later to a separate gmail/sheets specific file

def access_secret_version(project_id, secret_id, version_id="latest"):
    """Fetches the secret string from Google Cloud Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def authenticate():
    creds = None
    
    # 1. Try local file first (for your local development)
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    # 2. If no local file, pull from Secret Manager (for Cloud Run)
    if not creds:
        try:
            print("No local token.json found. Fetching from Secret Manager...")
            token_info = json.loads(access_secret_version(PROJECT_ID, SECRET_ID))
            creds = Credentials.from_authorized_user_info(token_info, SCOPES)
        except Exception as e:
            print(f"Could not load secret: {e}")
            return None

    # 3. Refresh the token if it's expired
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        
    return creds


def local_authenticate():
    """
    Authenticates and returns the credentials object
    """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

