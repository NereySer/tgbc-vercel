import pytest

from datetime import datetime, timezone, timedelta

from modules import time_checks
from modules.g_cal import Events
from modules.time_checks import DEFAULT_TIMEZONE, LATE_HOUR
from tests.tools import g_cal_event

def getTime(time):
    assert time.tzinfo==DEFAULT_TIMEZONE

    return time

def generate_event(hour, days_add):
    return g_cal_event(hour, days_add=days_add)

@pytest.mark.parametrize("set_hour, set_events_date, events, exp_raise", [
    (9, 0, [generate_event(10, 0)], False),
    (9, 1, [generate_event(10, 0)], True),
    (9, 0, [generate_event(10, 1)], True),
    (9, 0, [generate_event(10, 0), generate_event(11, 0)], False),
    (9, 0, [generate_event(11, 0), generate_event(10, 0)], False),
    (9, 0, [generate_event(10, 0), generate_event(11, 1)], True),
    (9, 1, [generate_event(10, 0), generate_event(11, 1)], True),
    (11, 1, [generate_event(10, 0), generate_event(11, 1)], False),
])
def test_isTimeToRemind_error_raising(monkeypatch, set_hour, set_events_date, events, exp_raise: bool):
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


    monkeypatch.setattr(time_checks, 'datetime', mock_datetime)

    events = Events(events, datetime.now(DEFAULT_TIMEZONE) + timedelta(days = set_events_date))

    if exp_raise:
        with pytest.raises(Exception):
            time_checks.isItTimeToRemind(events)
    else:
        time_checks.isItTimeToRemind(events)

@pytest.mark.parametrize("set_hour, events, set_events_date, expected", [
    #No events
    (9,  [], 0, False),
    (12, [], 0, False),
    (21, [], 0, False),
    #Morning reminders
    (9,  [generate_event(10, 0)], 0, True),
    (9,  [generate_event(11, 0)], 0, True),
    (9,  [generate_event(16, 0)], 0, True),
    (9,  [generate_event(17, 0)], 0, False),
    #Daytime reminders
    (11, [generate_event(17, 0)], 0, True),
    (12, [generate_event(17, 0)], 0, True),
    (12, [generate_event(23, 0)], 0, True),
    #Evening reminders
    (12, [generate_event(9, 1)], 1, False),
    (13, [generate_event(9, 1)], 1, True),
    (13, [generate_event(11, 1)], 1, True),
    (13, [generate_event(12, 1)], 1, False),
    #Events in deep future
    (9,  [generate_event(9, 2)], 2, False),
    (12, [generate_event(9, 2)], 2, False),
    (21, [generate_event(9, 2)], 2, False),
    #Check multiple
    (9,  [generate_event(10, 1), generate_event(11, 1), generate_event(15, 1)], 1, False),
    (12, [generate_event(10, 1), generate_event(11, 1), generate_event(15, 1)], 1, False),
    (21, [generate_event(10, 1), generate_event(11, 1), generate_event(15, 1)], 1, True),
    #Check running event
    (12, [generate_event(10, 0)], 0, False),
    #Check whole-day event
    (21, [generate_event(-1, 1)], 1, False),
    (9,  [generate_event(-1, 1)], 0, True),
    (9,  [generate_event(-1, 1), generate_event(10, 1), generate_event(11, 1), generate_event(15, 1)], 1, False),
    (12, [generate_event(-1, 1), generate_event(10, 1), generate_event(11, 1), generate_event(15, 1)], 1, False),
    (21, [generate_event(-1, 1), generate_event(10, 1), generate_event(11, 1), generate_event(15, 1)], 1, True),
    (9,  [generate_event(-1, 0), generate_event(17, 0)], 0, False),
    (12, [generate_event(-1, 0), generate_event(17, 0)], 0, True),
])
def test_isTimeToRemind_single_event(monkeypatch, set_hour, events, set_events_date, expected: bool):
    test_isTimeToRemind_with_date_single_event(monkeypatch, set_hour, events, set_events_date, expected, None)

@pytest.mark.parametrize("set_hour, events, set_events_date, expected, use_date", [
    #Events in deep future, but with date provided
    (9, [generate_event(10, 2)], 2, True, 2),
    (9, [generate_event(11, 2)], 2, True, 2),
    (9, [generate_event(16, 2)], 2, True, 2),
    (9, [generate_event(17, 2)], 2, False, 2),
])
def test_isTimeToRemind_with_date_single_event(monkeypatch, set_hour, events, set_events_date, expected: bool, use_date):
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

        @classmethod
        def combine(self, date, time, tzinfo):
            return datetime.combine(date, time, tzinfo)

    monkeypatch.setattr(time_checks, 'datetime', mock_datetime)

    events = Events(events, datetime.now(DEFAULT_TIMEZONE) + timedelta(days = set_events_date))

    if use_date is None:
        isTime, ret_events = time_checks.isItTimeToRemind(events)
    else:
        isTime, ret_events = time_checks.isItTimeToRemind(events, datetime.now(DEFAULT_TIMEZONE).replace(hour=set_hour) + timedelta(days = use_date))

    assert isTime == expected
    if isTime:
        assert ret_events == events

@pytest.mark.parametrize("events, events_diff, expected_hour, expected_day_diff", [
    ([generate_event(10, 2)], 2, 21, 1),
    ([generate_event(12, 2)], 2, 9, 2),
    ([generate_event(17, 2)], 2, 12, 2),
    ([generate_event(-1, 2), generate_event(10, 2)], 2, 21, 1),
    ([generate_event(-1, 2), generate_event(12, 2)], 2, 9, 2),
    ([generate_event(-1, 2), generate_event(17, 2)], 2, 12, 2),
    ([generate_event(-1, 2)], 2, 9, 2),
])
def test_whenTimeToRemind(events, events_diff, expected_hour, expected_day_diff):

    assert time_checks.whenTimeToRemind(Events(events,  datetime.now(DEFAULT_TIMEZONE) + timedelta(days = events_diff))) == \
        datetime.now(DEFAULT_TIMEZONE).replace(hour=expected_hour, minute = 0, second = 0, microsecond = 0) + timedelta(days = expected_day_diff)

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

