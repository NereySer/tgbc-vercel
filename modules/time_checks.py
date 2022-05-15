from datetime import datetime, timezone, timedelta

DEFAULT_TIMEZONE = timezone(timedelta(hours=+3))
LATE_HOUR = 12
EVENING_HOUR = 17

NOTIFICATIONS_HOURS = [9, 12, 21]

def get_event_start_time(event) -> datetime:
    start_time = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
    
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo = DEFAULT_TIMEZONE)
        
    return start_time

def removeOldEvents(events, now):
    if not events: return

    for event in events:
        event_datetime = get_event_start_time(event)
        
        if now > event_datetime: 
            events.remove(event)

def checkEvents(events):
    if not events: return (None, None)
        
    first_event_datetime = get_event_start_time(events[0])
    last_event_datetime = first_event_datetime

    for event in events:
        event_datetime = get_event_start_time(event)
        
        if event_datetime.date() != first_event_datetime.date():
            raise Exception("Events in different days are not allowed")
        
        first_event_datetime = min(event_datetime, first_event_datetime)
        last_event_datetime = max(event_datetime, last_event_datetime)
        
    return (first_event_datetime, last_event_datetime)

def isTodayTimeToRemind(first_event_datetime, now):
    #Today morning reminder OR daytime reminder
    return first_event_datetime.hour < EVENING_HOUR or now.hour >= LATE_HOUR - 1

def isTomorrowTimeToRemind(first_event_datetime, now):
    #Evening reminder for early tomorrow events
    return now.hour > LATE_HOUR and first_event_datetime.hour < LATE_HOUR

def isTimeToRemind(events, date = None) -> (bool, datetime): 
    now = datetime.now(DEFAULT_TIMEZONE) if date is None else date
    
    removeOldEvents(events, now)
    (first_event_datetime, last_event_datetime) = checkEvents(events)

    if not events: 
        return (False, now)
    
    match (first_event_datetime.date() - now.date()).days:
        case 0:
            return (isTodayTimeToRemind(first_event_datetime, now), last_event_datetime)
        case 1:
            return (isTomorrowTimeToRemind(first_event_datetime, now), last_event_datetime)
        case _:
            return (False, last_event_datetime)

def whenHourToRemind(events, date) -> datetime:
    notification_time = None
    
    for hour in reversed(NOTIFICATIONS_HOURS):
        test_time = date.replace(hour = hour)

        if isTimeToRemind(events.copy(), test_time)[0]:
            notification_time = test_time
        elif notification_time is not None:
            break

    return notification_time
        
def whenTimeToRemind(events) -> datetime:
    if not events:
        raise Exception("No events provided")
        
    notification_time = None
    
    for day_offset in range(0, 2):
        test_time = get_event_start_time(events[0]).replace(minute = 0, second = 0, microsecond = 0) - timedelta(days = day_offset)
        
        test_time = whenHourToRemind(events, test_time)
        
        if test_time is not None:
            notification_time = test_time
        elif notification_time is not None:        
            break
        
    return notification_time

def setDateToBeginOfDay(date):
    return date.replace(hour=0, minute=0, second=0, microsecond=0)
        
def getTimeBounds(start = None):
    if start is None:
        begin = datetime.now(DEFAULT_TIMEZONE)
    else:
        begin = start

    if begin.hour > LATE_HOUR:
        #Too late to remind about today's events, so let's look for tomorrow
        begin += timedelta(days = 1)
        begin = setDateToBeginOfDay(begin)
    
    end = begin.replace(hour=23, minute=59, second=59, microsecond=0)

    return ( begin, end )
