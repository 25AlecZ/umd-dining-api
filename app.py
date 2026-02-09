from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from src.parser import parse_meals_html
from src.client import fetch_menu_html

# Health test: http://127.0.0.1:5000/health
# Test link: http://127.0.0.1:5000/menu?location=16&dtdate=2026-02-10

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

    location_name = ""
    if (location == 16):
        location_name = "South Campus Dining Hall"
    elif (location == 19):
        location_name = "Yahentamitsi Dining Hall"
    elif (location == 51):
        location_name = "251 North"

    if location is None or not dtdate:
        return jsonify({"error": "Use /menu?location=16&dtdate=2/7/2026"}), 400

    html = fetch_menu_html(location, dtdate)
    meals = parse_meals_html(html)

    return jsonify({
        "location": location_name,
        "dtdate": dtdate,
        "meals": meals
    })

if __name__ == "__main__":
    app.run(debug=True)

        