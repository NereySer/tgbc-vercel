from datetime import datetime, timezone, timedelta

DEFAULT_TIMEZONE = timezone(timedelta(hours=+3))

def getStart():
    return datetime.utcnow().isoformat() + 'Z'

def getEnd(): 
    next_day = datetime.now(DEFAULT_TIMEZONE) + timedelta(days = 1)

    end_next_day = next_day.replace(hour=23, minute=59, second=59, microsecond=0)

    return end_next_day.astimezone(timezone.utc).isoformat() + 'Z'
