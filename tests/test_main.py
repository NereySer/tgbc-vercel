import main, os, pytest
from datetime import datetime, timezone
from tests.tools import g_cal_event
from modules.time_checks import DEFAULT_TIMEZONE

def test_static_files():
    tester = main.app.test_client()

    response = tester.get('/images/not_found.jpg')
    assert response.status_code == 404

    response = tester.get('/images/profile.jpg')
    assert response.status_code >= 200 and response.status_code <= 299

    response = tester.get('/css/not_found.css')
    assert response.status_code == 404

    response = tester.get('/css/bootstrap.min.css')
    assert response.status_code >= 200 and response.status_code <= 299


def test_raising():
    tester = main.app.test_client()

    response = tester.get('/check_events?key=WRONG_KEY')
    assert response.status_code == 404

    response = tester.get('/check_events?key='+os.getenv('CHECK_KEY'))

    print(response.text)

    assert response.status_code >= 200 and response.status_code <= 299

def test_notifications():
    tester = main.app.test_client()

    response = tester.get('/')

    print(response.text)

    assert response.status_code >= 200 and response.status_code <= 299

def getTime(field):
    return datetime.fromisoformat(field.get('dateTime', field.get('date'))).replace(tzinfo = DEFAULT_TIMEZONE)

@pytest.mark.parametrize("set_hour, events", [
    # Test no events
    (9, []),
    # Test single events
    (9, [
        g_cal_event(10, text = 'text'),
    ]),
    (9, [
        g_cal_event(13, text = 'text'),
    ]),
    (9, [
        g_cal_event(19, text = 'text'),
    ]),
    (9, [
        g_cal_event(10, days_add = 1, text = 'text'),
    ]),
    (9, [
        g_cal_event(13, days_add = 1, text = 'text'),
    ]),
    (9, [
        g_cal_event(21, days_add = 1, text = 'text'),
    ]),
    (9, [
        g_cal_event(-1,text = 'text')
    ]),
    #Test multiple events
    (9, [
        g_cal_event(10, text = 'text'),
        g_cal_event(13, text = 'text'),
        g_cal_event(21, text = 'text'),
    ]),
    (9, [
        g_cal_event(-1,text = 'text'),
        g_cal_event(13, text = 'text'),
        g_cal_event(21, text = 'text'),
    ]),
    (9, [
        g_cal_event(-1,text = 'text'),
        g_cal_event(10, text = 'text'),
        g_cal_event(21, text = 'text'),
    ]),
])
def test_mock_events(monkeypatch, set_hour, events):
    class mock_datetime:
        @classmethod
        def now(self, tz=None):
            return ( datetime.now(DEFAULT_TIMEZONE).replace(hour = set_hour).astimezone(tz) )

        @classmethod
        def utcnow(self):
            return ( self.now(timezone.utc) )

        @classmethod
        def fromisoformat(self, val):
            return datetime.fromisoformat(val)

        @classmethod
        def combine(self, date, time, tzinfo):
            return datetime.combine(date, time, tzinfo)

    class mock_event_result:
        def __init__(self, timeMin, timeMax):
            self.timeMin = datetime.fromisoformat(timeMin[:-1]).replace(tzinfo = timezone.utc)
            self.timeMax = datetime.fromisoformat(timeMax[:-1]).replace(tzinfo = timezone.utc)

        def get(self, par1, par2):
            events_ret = []

            for event in events:
                if getTime(event['start']) <= self.timeMax and \
                    getTime(event['end']) >= self.timeMin:
                    events_ret.append(event)

            return events_ret

    class mock_list:
        def __init__(self, timeMin, timeMax):
            self.timeMin = timeMin
            self.timeMax = timeMax

        def execute(self):
            return mock_event_result(self.timeMin, self.timeMax)

    class mock_events:
        @classmethod
        def list(self,
            calendarId,
            timeMin, timeMax,
            singleEvents,
            orderBy
        ):
            return mock_list(timeMin, timeMax)

    class mock_g_service:
        @classmethod
        def events(self):
            return mock_events

    monkeypatch.setattr(main.g_cal, 'g_service', mock_g_service)
    monkeypatch.setattr(main, 'datetime', mock_datetime)
    monkeypatch.setattr(main.time_checks, 'datetime', mock_datetime)

    config = main.config.Config()
    config.last_time = '0001-01-01T00:00:00+00:00'

    test_notifications()

    test_raising()
