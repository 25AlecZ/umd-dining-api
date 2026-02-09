from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from flask_caching import Cache
from src.parser import parse_meals_html
from src.client import fetch_menu_html

# Health test: http://127.0.0.1:5000/health
# Test link: http://127.0.0.1:5000/menu?location=16&dtdate=2026-02-10

app = Flask(__name__)

app.config["CACHE_TYPE"] = "SimpleCache"      # in-memory for development, replace with Redis later
app.config["CACHE_DEFAULT_TIMEOUT"] = 600     # 10 minutes
cache = Cache(app)


def menu_cache_key(location: int, date_key: str) -> str:
    # cache key should be stable and unique per request
    return f"menu:{location}:{date_key}"

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
    date = request.args.get("dtdate", type=str) # YYYY-MM-DD format converted to M/D/YYYY in client.py
    dtdate = request.args.get("dtdate", type=str) # Fallback
    refresh = request.args.get("refresh", type=int) == 1 # Allows for forced refresh

    location_name = ""
    if (location == 16):
        location_name = "South Campus Dining Hall"
    elif (location == 19):
        location_name = "Yahentamitsi Dining Hall"
    elif (location == 51):
        location_name = "251 North"

    if location is None:
        return jsonify({"error": "Missing location Use /menu?location=16&dtdate=1/1/2026"}), 400
    if not dtdate or not date:
        return jsonify({"error": "Missing date. Use /menu?location=16&dtdate=1/1/2026"}), 400

    date_key = date if date else dtdate
    key = menu_cache_key(location, date_key)

    if not refresh:
        cached = cache.get(key)
        if cached is not None:
            # print("CACHE HIT:", key)
            return jsonify(cached)
    
    # print("CACHE MISS:", key)

    try:
        html = fetch_menu_html(location, date=date)
        meals = parse_meals_html(html)
        playload = {
            "location": location_name, 
            "date": date, 
            "meals": meals}
        
        cache.set(key, playload) # Default 10 min timeout
        return jsonify(playload)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Can narrow this to requests exceptions and return 502
        return jsonify({"error": "Upstream request failed", "detail": str(e)}), 502

if __name__ == "__main__":
    app.run(debug=True)

        