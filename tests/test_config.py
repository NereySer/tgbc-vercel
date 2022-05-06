from modules.config import Config
from datetime import datetime

def test_work():
    now = datetime.now().isoformat()
    config = Config()

    config.last_time = now

    assert config.last_time == now
    
    config.last_time = '0000-00-00T00:00:00'
    
