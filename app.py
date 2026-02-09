from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from src.parser import parse_stations_html
from src.client import fetch_menu_html

# Health test: http://127.0.0.1:5000/health
# Test link: http://127.0.0.1:5000/menu?location=16&dtdate=2/7/2026

app = Flask(__name__)

@app.get("/health") # Quick test to see if server works
def health():
    return jsonify({"ok": True})


@app.get("/") # Home page
def home():
    return '<h1>Welcome to the UMD Dining API</h1><p>Use the /menu endpoint to get the dining menu for a specific date and location.</p>'

@app.get("/menu")
def menu():
    # call like: /menu?location=16&dtdate=2/7/2026
    location = request.args.get("location", type=int)
    dtdate = request.args.get("dtdate", type=str)

    if location is None or not dtdate:
        return jsonify({"error": "Use /menu?location=16&dtdate=2/7/2026"}), 400

    html = fetch_menu_html(location, dtdate)
    stations = parse_stations_html(html)

    return jsonify({
        "location": location,
        "dtdate": dtdate,
        "stations": stations
    })

if __name__ == "__main__":
    app.run(debug=True)

        