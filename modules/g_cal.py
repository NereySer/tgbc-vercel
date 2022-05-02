import os

import googleapiclient
from google.oauth2 import service_account
from googleapiclient.discovery import build

from datetime import datetime, timezone

SCOPES = ['https://www.googleapis.com/auth/calendar']

calendarId = os.getenv('GOOGLE_CALENDAR_ID')
SERVICE_ACCOUNT_FILE = 'key/civil-hash.json'

credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
g_service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

def format_datetime(val: datetime) -> str:
    return val.astimezone(timezone.utc).replace(tzinfo=None).isoformat() + 'Z'

def get_incomig_events(begin: datetime, end: datetime):
    events_result = g_service.events().list(calendarId=calendarId,
                                            timeMin=format_datetime(begin), timeMax=format_datetime(end),
                                            singleEvents=True,
                                            orderBy='startTime').execute()
    return events_result.get('items', [])
