import pytest

from modules import message_format

@pytest.mark.parametrize("events, expected", [
    ([{
        'summary': 'test',
        'start': {
            'dateTime': '2022-05-03T19:00:00+03:00'
        }
    }], '2022-05-03T19:00:00+03:00 test\n'),
    ([
        {
            'summary': 'test',
            'start': {
                'dateTime': '2022-05-03T19:00:00+03:00'
            }
        }, 
        {
            'summary': 'second_test',
            'start': {
                'dateTime': '2022-05-03T20:00:00+03:00'
            }
        }
    ], '2022-05-03T19:00:00+03:00 test\n2022-05-03T20:00:00+03:00 second_test\n')
])
def test_work(events, expected):
    assert message_format.format(events) == expected
    
