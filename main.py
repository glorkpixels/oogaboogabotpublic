from flask import Flask
import oogaboogabot

import atexit
from apscheduler.schedulers.background import BackgroundScheduler


def job():
    oogaboogabot.respondToTweet('tweet_ID.txt')
    print("Success")


scheduler = BackgroundScheduler()
scheduler.add_job(func=job, trigger="interval", seconds=60)
scheduler.start()

app = Flask(__name__)

@app.route("/")
def index():
    return "Follow @oogaboogabot!"


atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    app.run()