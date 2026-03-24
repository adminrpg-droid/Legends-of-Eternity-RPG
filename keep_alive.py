"""
Keep-alive server untuk Replit.
Replit menidurkan app jika tidak ada request HTTP.
Gunakan UptimeRobot atau cron-job.org untuk ping /health setiap 5 menit.
"""
from flask import Flask
from threading import Thread
import logging

app = Flask(__name__)
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)  # Suppress Flask request logs


@app.route("/")
def home():
    return "⚔️ Legends of Eternity Bot — Online!"


@app.route("/health")
def health():
    return {"status": "ok", "bot": "Legends of Eternity"}


def run():
    app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)


def keep_alive():
    t = Thread(target=run, daemon=True)
    t.start()
