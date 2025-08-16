from threading import Thread

from flask import Flask

from .config import ConfigManager

app = Flask(__name__)


@app.route("/")
def index():
    return "Alive"


def run():
    app.run(host="0.0.0.0", port=ConfigManager.get("PORT", 8000))


def check():
    t = Thread(target=run)
    t.start()
