from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import re

templates = {}
env = None

def initTemplate(name: str):
    global templates, env

    if env is None:
        env = Environment(
            loader=FileSystemLoader('templates'),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    if name not in templates:
        templates[name] = env.get_template(f'{name}.j2')
    
    return templates[name]

def getSlicedSummaries(events):
    pattern = re.compile('(?<=(?:- )|(?:, )|(?:: ))(?=.)')

    retVal = []

    for event in events:
        retVal.append(pattern.split(event['summary']))

    return retVal


def findCommon(list):
    if not list:
        return list

    retVal = list[0].copy()

    for i in range(1, len(list)):
        retVal = _getCommonTwo(retVal, list[i])

    return retVal

def _getCommonTwo(list1, list2) -> list:
    retVal = []

    for i in range(min(len(list1), len(list2))):
        if list1[i] == list2[i]:
            retVal.append(list1[i])
        else:
            break

    return retVal

def cutSummary(events, num):
    retEvents = []
    for event in events:
        event = event.copy()

        event['summary'] = event['summary'][num:]

        retEvents.append(event)

    return retEvents

def getMinMaxLen(list):
    if not list:
        return (0, 0)

    minLen = len(list[0])
    maxLen = minLen

    for i in range(1, len(list)):
        minLen = min(minLen, len(list[i]))
        maxLen = max(maxLen, len(list[i]))

    return (minLen, maxLen)

def splitCommonSummary(events):
    summaries = getSlicedSummaries(events)

    common_summary = findCommon(summaries)

    minLen, maxLen = getMinMaxLen(summaries)

    summaries_equal = False

    if len(common_summary) == minLen:
        if minLen == maxLen:
            summaries_equal = True
        else:
            common_summary.pop()

    common_summary = ''.join(common_summary)

    retEvents = cutSummary(events, len(common_summary))

    if not summaries_equal:
        common_summary = common_summary.strip()[:-1]

    return (common_summary.strip(), retEvents)

def telegram(events, diff) -> str:
    total_summary, events = splitCommonSummary(events)

    template = initTemplate('telegram_message')
    
    return template.render(total_summary=total_summary, events=events, diff=diff, datetime=datetime)

def notifications(content):
    template = initTemplate('index.html')
    
    return template.render(content=content)

def raise_notification(content, html:bool=True):
    template = initTemplate('raise.html' if html else 'raise')
    
    return template.render(content=content)
