import os
import signal
import telebot
from flask import Flask, request, send_from_directory, abort

from datetime import datetime, timedelta

from modules import *

bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))
app = Flask(__name__)

signal.signal(signal.SIGINT, lambda s, f: os._exit(0))

class Content(object):
    pass

def getNextEvents(now, begin_time):
    time_bounds = time_checks.getTimeBounds(begin_time)

    while not (events := g_cal.get_incomig_events( *time_bounds )):
        if time_bounds[0] - now > timedelta(days = 7):
            break

        time_bounds = (
            time_checks.setDateToBeginOfDay(time_bounds[0] + timedelta(days = 1)),
            time_bounds[1] + timedelta(days = 1)
        )

    return events

@app.route("/")
def show_next_notification():
    content = Content()

    content.now = datetime.now(time_checks.DEFAULT_TIMEZONE)

    content.config = config.Config()

    content.events = getNextEvents(content.now, datetime.fromisoformat(content.config.last_time))

    if content.events:
        content.now = time_checks.whenTimeToRemind(content.events)

        content.notification = message_format.telegram(content)

    return message_format.notifications(content)

@app.route("/images/<name>")
def get_image(name):

    try:
        return send_from_directory('images', name)
    except FileNotFoundError:
        abort(404)

@app.route("/css/<name>")
def get_css(name):

    try:
        return send_from_directory('css', name)
    except FileNotFoundError:
        abort(404)

@app.route("/check_events")
def check_events():
    if os.getenv('CHECK_KEY') != request.args.get('key', default = '', type = str):
        abort(404)

    content = Content()

    content.now = datetime.now(time_checks.DEFAULT_TIMEZONE)

    content.config = config.Config()

    content.time_bounds = time_checks.getTimeBounds(datetime.fromisoformat(content.config.last_time))

    content.events = g_cal.get_incomig_events( *content.time_bounds )

    content.isTime, content.events = time_checks.isItTimeToRemind(content.events)

    if content.isTime:
        bot.send_message(os.getenv('TELEGRAM_CHANNEL_ID'), message_format.telegram(content))

        content.config.last_time = str(time_checks.setDateToBeginOfDay(content.time_bounds[0] + timedelta(days=1)))

    return message_format.raise_notification(content)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.getenv('PORT')) # port 5000 is the default
