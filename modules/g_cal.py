import os

import googleapiclient
from google.oauth2 import service_account
from googleapiclient.discovery import build

from datetime import datetime, timezone

g_service = None

SCOPES = ['https://www.googleapis.com/auth/calendar']

calendarId = os.getenv('GOOGLE_CALENDAR_ID')
SERVICE_ACCOUNT_FILE = 'key/civil-hash.json'

class Events:
    def __init__(self, events = [], date = datetime.now()):
        self.total, self.timed = eventsSplitFormat(events)

        self.date = date

    def __eq__(self, other):
        return self.total == other.total and \
            self.timed == other.timed and \
            self.date == other.date

    def __repr__(self):
        return 'Events(' + str(self.total) + ', ' + str(self.timed) + ', ' + str(self.date) + ')'

    def __bool__(self):
        return bool(self.total) or bool(self.timed)

def getGService():
    global g_service
    
    if g_service is None:
        credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        g_service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

def format_datetime(val: datetime) -> str:
    return val.astimezone(timezone.utc).replace(tzinfo=None).isoformat() + 'Z'

def eventsSplitFormat(events):
    total_summaries = []
    ret_events = []

    for event in events:
        if 'date' in event['start']:
            total_summaries.append(event['summary'])
        else:
            event = event.copy()

            event['start'] = datetime.fromisoformat(event['start']['dateTime'])
            event['end'] = datetime.fromisoformat(event['end']['dateTime'])

            ret_events.append(event)

    return (total_summaries, ret_events)

def get_incomig_events(begin: datetime, end: datetime):
    if begin.date() != end.date():
        raise Exception("Events can be requested only per one day")

    getGService()

    events_result = g_service.events().list(calendarId=calendarId,
                                            timeMin=format_datetime(begin), timeMax=format_datetime(end),
                                            singleEvents=True,
                                            orderBy='startTime').execute()

    return Events(events_result.get('items', []), begin)
