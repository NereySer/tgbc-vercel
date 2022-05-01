import main

def test_work():
    tester = main.app.test_client()
    
    assert tester.get('/') is not None
