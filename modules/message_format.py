
def format(events) -> str:
    if not events:
        retval = 'No upcoming events found.\n'
    else:
        retval = ''
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            retval += start + ' ' + event['summary'] + '\n'
        
    return retval
