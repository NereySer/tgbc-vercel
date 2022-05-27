from datetime import datetime, timezone, timedelta
from copy import copy

DEFAULT_TIMEZONE = timezone(timedelta(hours=+3))
LATE_HOUR = 12
EVENING_HOUR = 17

NOTIFICATIONS_HOURS = [9, 12, 21]

def withoutOldEvents(timed_events, now):
    if not timed_events: return []

    ret_events = []

    for event in timed_events:
        if now <= event['start']:
            ret_events.append(event)

    return ret_events

def checkEvents(events):
    if not events.timed:
        if not events.total:
            return None
        else:
            return events.date.replace(hour = LATE_HOUR, minute = 0, second = 0, microsecond = 0)

    for event in events.timed:
        if event['start'].date() != events.date.date():
            raise Exception("Events in different days are not allowed")

    return min(events.timed, key = lambda event:event['start'])['start']

def isTodayTimeToRemind(first_event_datetime, now):
    #Today morning reminder OR daytime reminder
    return first_event_datetime.hour < EVENING_HOUR or now.hour >= LATE_HOUR - 1

def isTomorrowTimeToRemind(first_event_datetime, now):
    #Evening reminder for early tomorrow events
    return now.hour > LATE_HOUR and first_event_datetime.hour < LATE_HOUR

def isItTimeToRemind(events, date = None):
    events = copy(events)

    now = datetime.now(DEFAULT_TIMEZONE) if date is None else date

    events.timed = withoutOldEvents(events.timed, now)
    if not events:
        return (False, events)

    first_event_datetime = checkEvents(events)

    match (first_event_datetime.date() - now.date()).days:
        case 0:
            return (isTodayTimeToRemind(first_event_datetime, now), events)
        case 1:
            return (isTomorrowTimeToRemind(first_event_datetime, now), events)
        case _:
            return (False, events)

def whenHourToRemind(events, date) -> datetime:
    notification_time = None

    for hour in reversed(NOTIFICATIONS_HOURS):
        test_time = date.replace(hour = hour)

        if isItTimeToRemind(events, test_time)[0]:
            notification_time = test_time
        elif notification_time is not None:
            break

    return notification_time

def whenTimeToRemind(events) -> datetime:
    if not events:
        raise Exception("No events provided")

    notification_time = None

    for day_offset in range(0, 2):
        test_time =  events.date.replace(minute = 0, second = 0, microsecond = 0) - timedelta(days = day_offset)

        test_time = whenHourToRemind(events, test_time)

        if test_time is not None:
            notification_time = test_time
        elif notification_time is not None:
            break

    return notification_time

def setDateToBeginOfDay(date):
    return date.replace(hour=0, minute=0, second=0, microsecond=0)

def getTimeBounds(start = None):
    now = datetime.now(DEFAULT_TIMEZONE)

    if start is None:
        begin = now
    else:
        begin = max(now, start)

    if begin.hour > LATE_HOUR:
        #Too late to remind about today's events, so let's look for tomorrow
        begin += timedelta(days = 1)
        begin = setDateToBeginOfDay(begin)

    end = begin.replace(hour=23, minute=59, second=59, microsecond=0)

    return ( begin, end )
