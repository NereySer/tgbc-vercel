from datetime import datetime, timedelta
from modules.time_checks import DEFAULT_TIMEZONE

def g_cal_event(hour, days_add = 0, text = '', duration = 1, transparent = False, base_date = None):
    if base_date is None:
        base_date = datetime.now(DEFAULT_TIMEZONE)

    retVal = {
        'summary': text,
        'transparency': ('transparent' if transparent else 'opaque')
    }

    if hour == -1:
        start_time = base_date.date() + timedelta(days = days_add)

        delta_duration = timedelta(days = duration)

        key_name = 'date'
    else:
        start_time = base_date.replace(hour=hour) + timedelta(days = days_add)

        delta_duration = timedelta(hours = duration)

        key_name = 'dateTime'

    retVal['start'] = {
            key_name: start_time.isoformat()
    }

    retVal['end'] = {
            key_name: (start_time + delta_duration).isoformat()
    }

    return retVal
