import main

def test_work():
    tester = main.app.test_client()
    
    response = tester.get('/')
    
    assert response.status_code >= 200 and response.status_code <= 299
