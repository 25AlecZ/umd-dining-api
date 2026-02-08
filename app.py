from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Health test: http://127.0.0.1:5000/health
# Test link: http://127.0.0.1:5000/menu?location=16&dtdate=2/7/2026

app = Flask(__name__)

BASE_URL = 'https://nutrition.umd.edu/'

def fetch_menu_html(location_num: int, date: str) -> str:
    url = requests.get(BASE_URL, 
                       params={'locationNum': location_num, 'dtdate': date},
                       timeout = 20,
                       headers={'User-Agent': 'umd-dining-api'})
    url.raise_for_status()
    return url.text

def parse_stations_html(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    stations = []

    station_card = soup.find_all('div', class_='card')

    for station in station_card:
        station_name = station.find('h5', class_='card-title')
        if not station_name:
            continue
        station_name = station_name.get_text(strip=True)
        items = []
        for item in station.find_all('a', class_='menu-item-name'):
            item_name = item.get_text(strip=True)
            href = item.get('href') # Returns None if href is missing
            if not href:
                continue
            href = href.strip()

            rec = None
            if "RecNumAndPort=" in href:
                rec = href.split("RecNumAndPort=", 1)[1] #Splits into two parts, second part is RecNumAndPort value
            
            items.append({
                "name": item_name,
                "recNumAndPort": rec,
                "item_Url": urljoin(BASE_URL, href)  # full link
            })

        if items:
            stations.append({
                "station": station_name,
                "items": items
            })

    return stations

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

        