import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
BASE_URL = 'https://nutrition.umd.edu/'

def fetch_menu_html(location_num: int, date: str) -> str:
    url = requests.get(BASE_URL, 
                       params={'locationNum': location_num, 'dtdate': date},
                       timeout = 20,
                       headers={'User-Agent': 'umd-dining-api'})
    url.raise_for_status()
    return url.text