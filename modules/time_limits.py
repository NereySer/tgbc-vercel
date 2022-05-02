from datetime import datetime, timezone, timedelta

DEFAULT_TIMEZONE = timezone(timedelta(hours=+3))
LATE_HOUR = 12

def getTimeBounds():
    begin = datetime.now(DEFAULT_TIMEZONE)

    if begin.hour > LATE_HOUR:
        begin += timedelta(days = 1)
        begin = begin.replace(hour=0, minute=0, second=0, microsecond=0)
    
    end = begin.replace(hour=23, minute=59, second=59, microsecond=0)

    return {
        'begin': begin, 
        'end': end    
    }

