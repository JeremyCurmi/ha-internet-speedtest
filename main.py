import datetime
import logging
import time

import speedtest
from flask import Flask, jsonify
from flask_apscheduler import APScheduler

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

LOG_FILE = "log/logging.txt"
wifi = speedtest.Speedtest()
app = Flask(__name__)


def bytes_to_megabytes(bytes_: float) -> float:
    """Convert bytes to megabytes."""
    return round(bytes_ * (9.537 * 10 ** -7))


def current_timestamp() -> str:
    """Return current timestamp."""
    timestamp = time.time()
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def log_results(filepath: str, result: dict):
    """Write results to log file.

    :param filepath: log file path relative to project root
    :type filepath: str
    :param result: result to be written to log file
    :type result: dict
    """
    log_ = f"{current_timestamp()} : {str(result)} \n"
    with open(filepath, mode="a", encoding="utf-8") as file:
        file.write(log_)


def run_and_log_test() -> dict:
    """Run speedtest and log results.

    :return: results of speedtest
    :rtype: dict
    """
    wifi.get_best_server()
    wifi.download()
    wifi.upload()
    wifi.results.share()
    wifi.results.dict()
    results = wifi.results.dict()
    results["download"] = bytes_to_megabytes(results["download"])
    results["upload"] = bytes_to_megabytes(results["upload"])
    log_results(LOG_FILE, results)
    return results


def scheduled_task():
    """Run speedtest and log results."""
    _ = run_and_log_test()


@app.route("/")
def index():
    """Return index page."""
    return "Run internet speed test"


@app.route("/test")
def test():
    """Return results of speedtest."""
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
