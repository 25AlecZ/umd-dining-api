from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = 'https://nutrition.umd.edu/'

def parse_meals_html(html: str) -> list[dict]:
    soup = BeautifulSoup(html, 'html.parser')
    meals = []

    for meal_section in soup.select('a.nav-link[data-toggle="tab"]'):
        meal_name = meal_section.get_text(strip=True)
        meal_href = meal_section.get('href')  # Get href attribute
        if not meal_href or not meal_href.startswith('#'):
            continue

        meal_id = meal_href[1:]  # Remove # to get the id

        meal_div = soup.find(id=meal_id)
        if not meal_div:
            continue

        stations = parse_stations_html(meal_div)

        meals.append({
            "meal": meal_name,
            "stations": stations
        })

    return meals


def parse_stations_html(meal) -> list[dict]:
    stations = []
    for station in meal.select('div.card'):
        station_name = station.find('h5', class_='card-title')
        if not station_name:
            continue
        station_name = station_name.get_text(strip=True)
        
        items = parse_items_html(station)

        if items:
            stations.append({
                "station": station_name,
                "items": items
            })

    return stations

def parse_items_html(station):
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
            "item_url": urljoin(BASE_URL, href)  # full link
        })
    
    return items