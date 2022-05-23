from datetime import datetime, timezone, timedelta, date, time

DEFAULT_TIMEZONE = timezone(timedelta(hours=+3))
LATE_HOUR = 12
EVENING_HOUR = 17

NOTIFICATIONS_HOURS = [9, 12, 21]

def get_event_start_time(event):
    if 'dateTime' in event['start']:
        start_time = datetime.fromisoformat(event['start']['dateTime'])

        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo = DEFAULT_TIMEZONE)
    else:
        start_time = date.fromisoformat(event['start']['date'])
    
    return start_time

def removeOldEvents(events, now):
    if not events: return

    for event in events:
        event_datetime = get_event_start_time(event)
        
        if type(event_datetime) is not date and now > event_datetime: 
            events.remove(event)

def isDatesEqual(date1, date2):
    if type(date1) is not date:
        date1 = date1.date()

    if type(date2) is not date:
        date2 = date2.date()

    return date1 == date2

def minTime(date1, date2):
    if type(date1) is type(date2):
        return min(date1, date2)
    elif type(date1) is not date:
        return date1
    else:
        return date2

def maxTime(date1, date2):
    if type(date1) is type(date2):
        return max(date1, date2)
    elif type(date1) is not date:
        return date1
    else:
        return date2

def addTime(date1):
    if type(date1) is date:
        date1 = datetime.combine(date1, time(12, 0, 0), DEFAULT_TIMEZONE)

    return date1

def checkEvents(events):
    if not events: return (None, None)
        
    first_event_datetime = get_event_start_time(events[0])
    last_event_datetime = first_event_datetime

    for event in events:
        event_datetime = get_event_start_time(event)
        
        if not isDatesEqual(event_datetime, first_event_datetime):
            print(events)
            raise Exception("Events in different days are not allowed")
        
        first_event_datetime = minTime(event_datetime, first_event_datetime)
        last_event_datetime = maxTime(event_datetime, last_event_datetime)
        

    first_event_datetime = addTime(first_event_datetime)
    last_event_datetime = addTime(last_event_datetime)

    return (first_event_datetime, last_event_datetime)

def isTodayTimeToRemind(first_event_datetime, now):
    #Today morning reminder OR daytime reminder
    return first_event_datetime.hour < EVENING_HOUR or now.hour >= LATE_HOUR - 1

def isTomorrowTimeToRemind(first_event_datetime, now):
    #Evening reminder for early tomorrow events
    return now.hour > LATE_HOUR and first_event_datetime.hour < LATE_HOUR

def isTimeToRemind(events, date = None) -> (bool, datetime): 
    print(events)
    now = datetime.now(DEFAULT_TIMEZONE) if date is None else date
    print(now)
    
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
        test_time =  addTime(get_event_start_time(events[0])).replace(minute = 0, second = 0, microsecond = 0) - timedelta(days = day_offset)
        
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
