import time
import logging
import datetime
import speedtest
from flask import Flask, jsonify
from flask_apscheduler import APScheduler

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

LOG_FILE = "log/logging.txt"
wifi = speedtest.Speedtest()
app = Flask(__name__)


def bytes_to_megabytes(bytes: float) -> float:
    return round(bytes * (9.537 * 10 ** -7))


def current_timestamp() -> str:
    ts = time.time()
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def log_results(filepath: str, result: dict):
    log_ = f"{current_timestamp()} : {str(result)} \n"
    with open(filepath, "a") as file:
        file.write(log_)


def run_and_log_test() -> dict:
    download = bytes_to_megabytes(wifi.download())
    upload = bytes_to_megabytes(wifi.upload())
    results = {"download": download, "upload": upload}
    log_results(LOG_FILE, results)
    return results


def scheduled_task():
    _ = run_and_log_test()


@app.route("/")
def index():
    return "Run internet speed test"


@app.route("/test")
def test():
    results = run_and_log_test()
    return jsonify(results)


if __name__ == "__main__":
    scheduler = APScheduler()
    scheduler.add_job(
        id="run internet speed test",
        func=scheduled_task,
        trigger="interval",
        seconds=3600,
    )
    scheduler.start()
    app.run(port=5001)
