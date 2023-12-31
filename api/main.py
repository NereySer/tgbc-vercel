import os
import signal
import telebot
from flask import Flask, request, send_from_directory, abort
import redis

from datetime import datetime, timedelta

from modules import *

bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))
app = Flask(__name__)

signal.signal(signal.SIGINT, lambda s, f: os._exit(0))

config_prefix = os.getenv('DEPLOY')

class Content(object):
    pass

def getNextEvents(now, begin_time):
    events_col = []

    time_bounds = time_checks.getTimeBounds(begin_time)

    while time_bounds[0] - now <= timedelta(days = 7):
        events = g_cal.get_incomig_events( *time_bounds )

        if events:
            events_col.append(events)

        time_bounds = (
            time_checks.setDateToBeginOfDay(time_bounds[0] + timedelta(days = 1)),
            time_bounds[1] + timedelta(days = 1)
        )

    return events_col

@app.route("/")
def show_next_notifications():
    content = Content()

    content.now = datetime.now(time_checks.DEFAULT_TIMEZONE)

    content.config = config_redis.Config(config_prefix)

    events_col = getNextEvents(content.now, datetime.fromisoformat(content.config.last_time))

    content.notifications = []

    for events in events_col:
        notification = Content()

        notification.events = events
        notification.time = time_checks.whenTimeToRemind(events)
        notification.text = message_format.telegram(notification)

        content.notifications.append(notification)

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

    content.time = datetime.now(time_checks.DEFAULT_TIMEZONE)

    content.config = config_redis.Config(config_prefix)

    content.time_bounds = time_checks.getTimeBounds(datetime.fromisoformat(content.config.last_time))

    content.events = g_cal.get_incomig_events( *content.time_bounds )

    content.isTime, content.events = time_checks.isItTimeToRemind(content.events)

    if content.isTime:
        bot.send_message(os.getenv('TELEGRAM_CHANNEL_ID'), message_format.telegram(content))

        content.config.last_time = str(time_checks.setDateToBeginOfDay(content.time_bounds[0] + timedelta(days=1)))

    return message_format.raise_notification(content)

@app.route("/check_redis")
def check_redis():
    r = redis.Redis.from_url(
        os.getenv('KV_URL').replace("redis://", "rediss://"),
        charset="utf-8",
        decode_responses=True)

    if not r.exists("test"):
        r.set('test',1)

    last = r.get('test')
    r.set('test',int(last)+1, ex=15)
    current = r.get('test')

    r.delete('test_last_time')

    return f"""{last}
             {current}
              redis test done"""
    
@app.route("/redis_creds")
def redis_creds():
    return f"""{os.getenv('KV_URL')}
             {os.getenv('KV_REST_API_URL')}
             {os.getenv('KV_REST_API_TOKEN')}
             {os.getenv('KV_REST_API_READ_ONLY_TOKEN')}
              redis test done"""

@app.route("/redis_config")
def redis_config():
    config = config_redis.Config("dev")

    last = config.last_time
    config.last_time = '0002-01-01T00:00:00+00:00'
    current = config.last_time

    return f"""{last}
             {current}
              redis test done"""
    
    return config.last_time

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.getenv('PORT')) # port 5000 is the default
