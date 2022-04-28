import unittest

from datetime import datetime, timezone, timedelta
from modules import time_limits as t

def test_start_time():
    timeStart = t.getStart()

    assert timeStart[-1]=='Z'
    assert abs(datetime.fromisoformat(timeStart[:-1])-datetime.utcnow())<timedelta(seconds = 1)

def test_end_time():
    timeEnd = t.getEnd()
    
    assert timeEnd[-1]=='Z'
    
    timeEnd = datetime.fromisoformat(timeEnd[:-1]).astimezone(t.DEFAULT_TIMEZONE)
    
    assert timeEnd.hour==23
    assert timeEnd.minute==59
    assert timeEnd.second==59
    
def test_time_difference():
    timeStart = t.getStart()
    timeEnd = t.getEnd()
    
    timeStart = datetime.fromisoformat(timeStart[:-1]).astimezone(t.DEFAULT_TIMEZONE)
    timeEnd = datetime.fromisoformat(timeEnd[:-1]).astimezone(t.DEFAULT_TIMEZONE)
    
    diff = timeEnd - timeStart
    
    assert timeEnd >= timeStart
    assert (timeEnd - timeStart) < timedelta(days = 2)
