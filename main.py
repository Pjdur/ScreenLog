from flask import Flask, jsonify, send_from_directory, request
import json
from datetime import datetime, timezone
from collections import defaultdict
import os

app = Flask(__name__)

EVENTS_FILE = "events.jsonl"
SCREENSHOTS_DIR = "screenshots"

@app.route("/api/summary")
def summary():
    date_str = request.args.get("date")
    if date_str:
        date = datetime.fromisoformat(date_str).date()
    else:
        date = datetime.now(timezone.utc).date()

    totals = defaultdict(float)
    with open(EVENTS_FILE) as f:
        for line in f:
            e = json.loads(line)
            if datetime.fromisoformat(e["start"]).date() == date:
                totals[e["app"]] += e["duration_s"]

    return jsonify(dict(sorted(totals.items(), key=lambda x: x[1], reverse=True)))

@app.route("/api/screenshots")
def screenshots():
    if not os.path.isdir(SCREENSHOTS_DIR):
        return jsonify([])
    files = sorted(os.listdir(SCREENSHOTS_DIR), reverse=True)
    return jsonify(files)

@app.route("/api/screenshots/<path:name>")
def screenshot_file(name):
    return send_from_directory(SCREENSHOTS_DIR, name)

@app.route("/")
def dashboard():
    return send_from_directory("static", "index.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)   