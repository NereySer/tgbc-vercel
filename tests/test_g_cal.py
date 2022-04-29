import unittest

from datetime import datetime, timezone, timedelta
from modules import g_cal

def test_work():
    assert g_cal.get_incomig_events() is not None
