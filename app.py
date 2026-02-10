from flask import Flask, jsonify, request
from flask_caching import Cache
from src.parser import parse_meals_html
from src.client import fetch_menu_html

import datetime

# Health test: http://127.0.0.1:5000/health
# Test link: http://127.0.0.1:5000/menu?location=16&date=2026-02-10

app = Flask(__name__)

app.config["CACHE_TYPE"] = "SimpleCache"      # in-memory for development, replace with Redis later
app.config["CACHE_DEFAULT_TIMEOUT"] = 600     # 10 minutes
cache = Cache(app)

LOCATION_MAP = {
    16: "South Campus Dining Hall",
    19: "Yahentamitsi Dining Hall",
    51: "251 North",
}


def menu_cache_key(location: int, date_key: str) -> str:
    # cache key should be stable and unique per request
    return f"menu:{location}:{date_key}"

def week_menu_cache_key(location: int, date_key: str) -> str:
    # cache key should be stable and unique per request
    return f"week_menu:{location}:{date_key}"

@app.get("/health") # Quick test to see if server works
def health():
    return jsonify({"ok": True})


@app.get("/") # Home page
def home():
    return '<h1>Welcome to the UMD Dining API</h1><p>Use the /menu endpoint to get the dining menu for a specific date and location.</p>'

@app.get("/locations") # Returns allowed locations
def locations():
    locations = [
        {
            "id": 16,
            "name": "South Campus Dining Hall"
        },
        {
            "id": 19,
            "name": "Yahentamitsi Dining Hall"
        },
        {
            "id": 51,
            "name": "251 North"
        }
    ]
    return jsonify(locations)

@app.get("/menu")
def menu():
    # call like: /menu?location=16&date=2026-02-10
    location = request.args.get("location", type=int)
    date = request.args.get("date", type=str) # YYYY-MM-DD format converted to M/D/YYYY in client.py
    refresh = request.args.get("refresh", type=int) == 1 # Allows for forced refresh

    if location is None:
        return jsonify({"error": "Missing location Use /menu?location=16&date=2026-01-01"}), 400
    if location not in LOCATION_MAP:
        return jsonify({"error": "Invalid location. Allowed: 16, 19, 51"}), 400
    if not date:
        return jsonify({"error": "Missing date. Use /menu?location=16&date=2026-01-01"}), 400
    
    location_name = LOCATION_MAP[location]

    key = menu_cache_key(location, date)

    if not refresh:
        cached = cache.get(key)
        if cached is not None:
            # print("CACHE HIT:", key)
            return jsonify(cached)
    
    # print("CACHE MISS:", key)

    try:
        html = fetch_menu_html(location, date=date)
        meals = parse_meals_html(html)
        payload = {
            "location_name": location_name, 
            "location_id": location,
            "date": date, 
            "meals": meals}
        cache.set(key, payload) # Default 10 min timeout
        return jsonify(payload)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Can narrow this to requests exceptions and return 502
        return jsonify({"error": "Upstream request failed", "detail": str(e)}), 502
    
@app.get("/week") # returns a week of menus
def week():
    # call like: /week?location=16
    location = request.args.get("location", type=int)
    refresh = request.args.get("refresh", type=int) == 1 # Allows for forced refresh

    start_date = datetime.date.today() # Always displays a week from today, website only shows a week of menus
    dates = [(start_date + datetime.timedelta(days=i)).isoformat() for i in range(7)]


    if location is None:
        return jsonify({"error": "Missing location Use /week?location=16"}), 400
    if location not in LOCATION_MAP:
        return jsonify({"error": "Invalid location. Allowed: 16, 19, 51"}), 400
    
    location_name = LOCATION_MAP[location]


    key = week_menu_cache_key(location, dates[0]) # Cache key based on first date

    if not refresh:
        cached = cache.get(key)
        if cached is not None:
            # print("CACHE HIT:", key)
            return jsonify(cached)
    
    # print("CACHE MISS:", key)

    try:
        week_payload = {
            "location_name": location_name, 
            "location_id": location,
            "start_date": dates[0],
            "days": []
        }
        for date in dates:
            day_key = menu_cache_key(location, date)
            day_cached = None if refresh else cache.get(day_key) # Check if refresh = 1, if it is then fetch new data

            if day_cached is not None:
                #print("DAY CACHE HIT:", day_key["date"])
                day_payload = {
                    "date": day_cached["date"],
                    "meals": day_cached["meals"]
                }
            else:
                #print("CACHE MISS:", day_key["date"])
                html = fetch_menu_html(location, date=date)
                meals = parse_meals_html(html)

                full_menu_payload = {
                    "location_name": location_name,
                    "location_id": location,
                    "date": date,
                    "meals": meals
                }

                cache.set(day_key, full_menu_payload) # Cache individual day for future week requests

                day_payload = {
                    "date": date,
                    "meals": meals
                }
                
            week_payload["days"].append(day_payload)
        cache.set(key, week_payload) # Default 10 min timeout
        return jsonify(week_payload)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Can narrow this to requests exceptions and return 502
        return jsonify({"error": "Upstream request failed", "detail": str(e)}), 502

if __name__ == "__main__":
    app.run(debug=True)

        