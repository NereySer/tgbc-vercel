from datetime import datetime, timedelta

from modules import g_cal

def test_work():
    assert g_cal.get_incomig_events(
        begin = datetime.utcnow(), 
        end = (datetime.utcnow() + timedelta(days = 1))
    ) is not None
