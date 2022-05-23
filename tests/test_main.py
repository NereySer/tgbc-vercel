import main, os, pytest
from tests.tools import g_cal_event

def test_static_files():
    tester = main.app.test_client()
    
    response = tester.get('/images/not_found.jpg')
    assert response.status_code == 404
    
    response = tester.get('/images/profile.jpg')
    assert response.status_code >= 200 and response.status_code <= 299
    
    response = tester.get('/css/not_found.css')
    assert response.status_code == 404
    
    response = tester.get('/css/bootstrap.min.css')
    assert response.status_code >= 200 and response.status_code <= 299


def test_raising():
    tester = main.app.test_client()
    
    response = tester.get('/check_events?key=WRONG_KEY')
    assert response.status_code == 404
    
    response = tester.get('/check_events?key='+os.getenv('CHECK_KEY'))
    assert response.status_code >= 200 and response.status_code <= 299

def test_notifications():
    tester = main.app.test_client()

    response = tester.get('/')

    print(response.text)

    assert response.status_code >= 200 and response.status_code <= 299

@pytest.mark.parametrize("events", [
    # Test no events
    ([]),
    # Test single events
    ([
        g_cal_event(10, text = 'text'),
    ]),
    ([
        g_cal_event(13, text = 'text'),
    ]),
    ([
        g_cal_event(19, text = 'text'),
    ]),
    ([
        g_cal_event(10, days_add = 1, text = 'text'),
    ]),
    ([
        g_cal_event(13, days_add = 1, text = 'text'),
    ]),
    ([
        g_cal_event(21, days_add = 1, text = 'text'),
    ]),
    ([
        g_cal_event(-1, text = 'text'),
    ]),
    #Test multiple events
    ([
        g_cal_event(10, text = 'text'),
        g_cal_event(13, text = 'text'),
        g_cal_event(21, text = 'text'),
    ]),
    ([
        g_cal_event(-1, text = 'text'),
        g_cal_event(13, text = 'text'),
        g_cal_event(21, text = 'text')
    ]),
    ([
        g_cal_event(10, text = 'text'),
        g_cal_event(-1, text = 'text'),
        g_cal_event(21, text = 'text'),
    ]),
])
def test_mock_events(monkeypatch, events):
    def mock_g_cal_get_incomig_events(begin, end):
        return events

    monkeypatch.setattr(main.g_cal, 'get_incomig_events', mock_g_cal_get_incomig_events)

    test_notifications()

    test_raising()
