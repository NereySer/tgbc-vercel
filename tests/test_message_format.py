import pytest

from modules import message_format
from datetime import datetime, timedelta

def generate_event(hour, text):
    return {
        'summary': text,
        'start': {
            'dateTime': f"2022-05-03T{hour}:00:00+03:00"
        }
    }
    
@pytest.mark.parametrize("events, diff, expected", [
    ([
        generate_event(19, 'test')
    ], 0, 'Сегодня, вторник, test в 19:00'),
    ([
        generate_event(19, 'test')
    ], 1, 'Завтра, вторник, test в 19:00'),
    ([
        generate_event(19, 'test'),
        generate_event(20, 'second_test')
    ], 0, 'Сегодня, вторник\n19:00 - test\n20:00 - second_test'),
    #Test agregation
    ([
        generate_event(19, 'test'),
        generate_event(20, 'test')
    ], 0, 'Сегодня, вторник, test в 19:00 и 20:00'),
    ([
        generate_event(11, 'test'),
        generate_event(15, 'test'),
        generate_event(19, 'test'),
        generate_event(20, 'test')
    ], 0, 'Сегодня, вторник, test в 11:00, 15:00, 19:00 и 20:00'),
    ([
        generate_event(19, 'test - first'),
        generate_event(20, 'test - second_test')
    ], 0, 'Сегодня, вторник, test\n19:00 - first\n20:00 - second_test'),
    ([
        generate_event(19, 'test - t - first'),
        generate_event(20, 'test - t - second_test'),
        generate_event(21, 'test - 3_test'),
        generate_event(22, 'test - 4_test')
    ], 0, 'Сегодня, вторник, test\n19:00 - t - first\n20:00 - t - second_test\n21:00 - 3_test\n22:00 - 4_test'),
    ([
        generate_event(19, 'test: first'),
        generate_event(20, 'test: second_test')
    ], 0, 'Сегодня, вторник, test\n19:00 - first\n20:00 - second_test')
])
def test_work(events, diff, expected):
    assert message_format.telegram(events, diff) == expected
