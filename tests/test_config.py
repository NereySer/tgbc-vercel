from modules.config import Config
from datetime import datetime

def test_work():
    now = datetime.now().isoformat()
    config = Config()
    
    tmp = config.last_time

    config.last_time = now

    assert config.last_time == now
    
    config.last_time = tmp
