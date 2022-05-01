import pytest

from datetime import datetime, timezone, timedelta

from modules import time_limits

def getTime(time):
    assert time[-1]=='Z'
    
    time_f = datetime.fromisoformat(time[:-1])
    
    assert time_f.tzinfo==None
    
    return time_f.replace(tzinfo=timezone.utc).astimezone(time_limits.DEFAULT_TIMEZONE)

@pytest.mark.parametrize("set_hour", [9, 10, 12, 13, 23])
def test_time_bounds(monkeypatch, set_hour):
    days_diff = 1 if set_hour > time_limits.LATE_HOUR else 0
    
    class mock_datetime:
        @classmethod
        def now(self, tz=None):
            return ( datetime.now(time_limits.DEFAULT_TIMEZONE).replace(hour=set_hour).astimezone(tz) )
        @classmethod
        def utcnow(self):
            return ( self.now(timezone.utc) )
    
    monkeypatch.setattr(time_limits, 'datetime', mock_datetime)
    
    now = time_limits.datetime.now(time_limits.DEFAULT_TIMEZONE)
    assert now.hour==set_hour

    time_bounds = time_limits.getTimeBounds()
    
    timeBegin = getTime(time_bounds['begin'])
    timeEnd = getTime(time_bounds['end'])
    
    if days_diff == 0:
        assert abs(timeBegin - now) < timedelta(seconds = 1)
    else:
        assert timeBegin > now + timedelta(days = days_diff-1)
        assert timeBegin < now + timedelta(days = days_diff)

        assert timeBegin.hour==0
        assert timeBegin.minute==0
        assert timeBegin.second==0
        
    assert timeEnd.hour==23
    assert timeEnd.minute==59
    assert timeEnd.second==59
    
    assert timeEnd > timeBegin
    assert (timeEnd - timeBegin) < timedelta(days = 1)
    
