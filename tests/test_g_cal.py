import unittest

from datetime import datetime, timezone, timedelta

from modules import g_cal
from modules import time_limits

def test_work():
    assert g_cal.get_incomig_events(
        begin = time_limits.getStart(), 
        end = time_limits.getEnd()
    ) is not None
