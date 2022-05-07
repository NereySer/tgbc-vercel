import os
import signal
import telebot
from flask import Flask

from datetime import datetime

from modules import *

bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))
app = Flask(__name__)

signal.signal(signal.SIGINT, lambda s, f: os._exit(0))

class Content(object):
    pass

@app.route("/")
def check_events():
    content = Content()
    
    content.now = datetime.now(time_checks.DEFAULT_TIMEZONE)
    
    content.config = config.Config()
    
    content.time_bounds = time_checks.getTimeBounds()
    
    content.events = g_cal.get_incomig_events( *content.time_bounds )
    
    content.isTime, content.last_event = time_checks.isTimeToRemind(content.events)
    
    content.should_remind = content.isTime and datetime.fromisoformat(content.config.last_time) < content.last_event
    
    if content.should_remind:
        bot.send_message( os.getenv('TELEGRAM_CHANNEL_ID'), message_format.telegram(content.events, (content.last_event.date()-content.now.date()).days))
        
        content.config.last_time = str(content.last_event)
    
    return message_format.web(content)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.getenv('PORT')) # port 5000 is the default
