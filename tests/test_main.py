import main, os
from tests import test_message_format

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

def test_notifications(monkeypatch):
    tester = main.app.test_client()
    
    response = tester.get('/')
    assert response.status_code >= 200 and response.status_code <= 299
    
    print(response.text)
    
    mock_events = []

    def mock_g_cal_get_incomig_events(begin, end):
        return mock_events
    
    monkeypatch.setattr(main.g_cal, 'get_incomig_events', mock_g_cal_get_incomig_events)

    response = tester.get('/')
    assert response.status_code >= 200 and response.status_code <= 299
    
    print(response.text)

    mock_events = [test_message_format.generate_event(10, 'test event')]

    response = tester.get('/')
    assert response.status_code >= 200 and response.status_code <= 299
    
    print(response.text)
