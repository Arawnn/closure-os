from datetime import datetime, timedelta, timezone
from pathlib import Path
import warnings

warnings.filterwarnings("ignore", category=FutureWarning, module="google.api_core")


from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class CalendarClient:
    def __init__(self, credentials_path: Path):
        token_path = credentials_path.parent / "token.json"
        
        creds = None
        if token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
            except ValueError:
                print(f"⚠ Token file is invalid, will re-authenticate")
                token_path.unlink()
                creds = None

        if not creds or not creds.valid:
            if not credentials_path.exists():
                raise FileNotFoundError(
                    f"Credentials file not found: {credentials_path}. "
                    "Please download it from Google Cloud Console."
                )
            print("🔐 Google authentication required")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES
            )

            creds = flow.run_local_server(port=0, open_browser=False)
            token_path.write_text(creds.to_json())
            print("✓ Authentication successful, token saved")

        self.service = build("calendar", "v3", credentials=creds)

    def create_event(
        self,
        calendar_id: str,
        title: str,
        description: str,
        start: datetime,
        duration_minutes: int,
    ):
        end = start + timedelta(minutes=duration_minutes)

        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)

        event = {
            "summary": title,
            "description": description,
            "start": {"dateTime": start.isoformat(), "timeZone": str(start.tzinfo)},
            "end": {"dateTime": end.isoformat(), "timeZone": str(end.tzinfo)},
        }

        return (
            self.service.events()
            .insert(calendarId=calendar_id, body=event)
            .execute()
        )