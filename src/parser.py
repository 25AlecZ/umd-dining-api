from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
BASE_URL = 'https://nutrition.umd.edu/'


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