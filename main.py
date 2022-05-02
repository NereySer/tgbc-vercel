import os
import signal
import telebot
from flask import Flask

from modules import *

bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))
app = Flask(__name__)

signal.signal(signal.SIGINT, lambda s, f: os._exit(0))

@app.route("/")
def check_events():
    content = []
    
    time_bounds = time_checks.getTimeBounds()
    content.append(time_bounds)
    
    events = g_cal.get_incomig_events(
        begin = time_bounds['begin'], 
        end = time_bounds['end']
    )
    content.append(events)
    
    isTime = time_checks.isTimeToRemind(events)
    content.append('Is time: ' + str(isTime) )
    
    bot.send_message(os.getenv('TELEGRAM_CHANNEL_ID'), message_format.format(events))
    
    page = '<html><body><p>'
    page += str(content).replace('\n', '</br>')
    page += '</p></body></html>'
    return page

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.getenv('PORT')) # port 5000 is the default
