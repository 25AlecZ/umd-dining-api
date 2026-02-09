import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import datetime
BASE_URL = 'https://nutrition.umd.edu/'
ALLOWED_LOCATIONS = {16, 19, 51} # South Campus, Yahentamitsi Dining Hall, 251 North id numbers

def date_format_change(d: datetime.date) -> str:
    return f"{d.month}/{d.day}/{d.year}"

def validate_location(location_num: int) -> None:
    if location_num not in ALLOWED_LOCATIONS:
        raise ValueError(f"Invalid location. Allowed: {sorted(ALLOWED_LOCATIONS)}")
    
def validate_date(date_str: str) -> None: # Must be within next week (7 days)
    try:
        d = datetime.date.fromisoformat(date_str)
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD.")

    today = datetime.date.today()
    last = today + datetime.timedelta(days=6)

    if not (today <= d <= last):
        raise ValueError(f"Date out of range. Available menus: {today} to {last}.")

    return d


def fetch_menu_html(location_num: int, date: str) -> str:
    validate_location(location_num)
    d = validate_date(date)
    dtdate = date_format_change(d)
    url = requests.get(
        BASE_URL, 
        params={'location': location_num, 'dtdate': dtdate},
        timeout = 20,
        headers={'User-Agent': 'umd-dining-api'}
    )
    url.raise_for_status()
    return url.text