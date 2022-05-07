import pytest

from datetime import datetime, timezone, timedelta

from modules import time_checks
from modules.time_checks import DEFAULT_TIMEZONE, LATE_HOUR

def getTime(time):
    assert time.tzinfo==DEFAULT_TIMEZONE
    
    return time

def generate_event(hour, days_add):
    if hour == -1:
        return {
            'start': {
                'date': (datetime.now(DEFAULT_TIMEZONE).date() + timedelta(days = days_add)).isoformat()
            }
        }
    else:
        return {
            'start': {
                'dateTime': (datetime.now(DEFAULT_TIMEZONE).replace(hour=hour) + timedelta(days = days_add)).isoformat()
            }
        }

@pytest.mark.parametrize("set_hour, events, exp_raise", [
    (9, [generate_event(10, 0)], False),
    (11, [generate_event(10, 0)], False),
    (9, [generate_event(10, 0), generate_event(11, 0)], False),
    (9, [generate_event(11, 0), generate_event(10, 0)], False),
    (9, [generate_event(10, 0), generate_event(11, 1)], True),
    (9, [generate_event(-1, 0)], False)
])
def test_isTimeToRemind_error_raising(monkeypatch, set_hour, events, exp_raise: bool):
    class mock_datetime:
        @classmethod
        def now(self, tz=None):
            return ( datetime.now(DEFAULT_TIMEZONE).replace(hour=set_hour).astimezone(tz) )
        
        @classmethod
        def utcnow(self):
            return ( self.now(timezone.utc) )
        
        @classmethod
        def fromisoformat(self, val):
            return datetime.fromisoformat(val)
    
    monkeypatch.setattr(time_checks, 'datetime', mock_datetime)
    
    if exp_raise:
        with pytest.raises(Exception):
            time_checks.isTimeToRemind(events)
    else:
        time_checks.isTimeToRemind(events)

@pytest.mark.parametrize("set_hour, events, expected", [
    #No events
    (9, [], False),
    (12, [], False),
    (21, None, False),
    #Morning reminders
    (9, [generate_event(10, 0)], True),
    (9, [generate_event(11, 0)], True),
    (9, [generate_event(16, 0)], True),
    (9, [generate_event(17, 0)], False),
    #Daytime reminders
    (11, [generate_event(17, 0)], True),
    (12, [generate_event(17, 0)], True),
    (12, [generate_event(23, 0)], True),
    #Evening reminders
    (12, [generate_event(9, 1)], False),
    (13, [generate_event(9, 1)], True),
    (13, [generate_event(11, 1)], True),
    (13, [generate_event(12, 1)], False),
    #Events in deep future
    (9, [generate_event(9, 2)], False),
    (12, [generate_event(9, 2)], False),
    (21, [generate_event(9, 2)], False),
    #Check multiple
    (9, [generate_event(10, 0), generate_event(11, 0), generate_event(15, 0)], True),
    #Check running event
    (9, [generate_event(-1, 0)], False)
])
def test_isTimeToRemind_single_event(monkeypatch, set_hour, events, expected: bool):
    class mock_datetime:
        @classmethod
        def now(self, tz=None):
            return ( datetime.now(DEFAULT_TIMEZONE).replace(hour=set_hour).astimezone(tz) )
        
        @classmethod
        def utcnow(self):
            return ( self.now(timezone.utc) )
        
        @classmethod
        def fromisoformat(self, val):
            return datetime.fromisoformat(val)
    
    monkeypatch.setattr(time_checks, 'datetime', mock_datetime)
    
    isTime, last_event = time_checks.isTimeToRemind(events)
    
    assert isTime == expected
    if isTime:
        assert last_event == datetime.fromisoformat(events[len(events)-1]['start']['dateTime'])
    
@pytest.mark.parametrize("set_hour", [9, 10, 12, 13, 23])
def test_time_bounds(monkeypatch, set_hour):
    days_diff = 1 if set_hour > LATE_HOUR else 0
    
    class mock_datetime:
        @classmethod
        def now(self, tz=None):
            return ( datetime.now(DEFAULT_TIMEZONE).replace(hour=set_hour).astimezone(tz) )
        @classmethod
        def utcnow(self):
            return ( self.now(timezone.utc) )
    
    monkeypatch.setattr(time_checks, 'datetime', mock_datetime)
    
    now = time_checks.datetime.now(DEFAULT_TIMEZONE)
    assert now.hour==set_hour

    timeBegin, timeEnd = time_checks.getTimeBounds()
    
    timeBegin = getTime(timeBegin)
    timeEnd = getTime(timeEnd)
    
    if days_diff == 0:
        assert abs(timeBegin - now) < timedelta(seconds = 1)
    else:
        assert timeBegin.date() == now.date() + timedelta(days = days_diff)

        assert timeBegin.hour==0
        assert timeBegin.minute==0
        assert timeBegin.second==0
        
    assert timeEnd.hour==23
    assert timeEnd.minute==59
    assert timeEnd.second==59
    
    assert timeEnd > timeBegin
    assert timeEnd.date() == timeBegin.date()
    
