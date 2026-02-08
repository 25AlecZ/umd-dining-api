import requests
from bs4 import BeautifulSoup
import datetime
import time


def main():
    
    url = 'https://nutrition.umd.edu/' #base URL

    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(days=6) # Full week of menus
    delta = end_date - start_date

    urls_to_scrape = []
    ''' for i in (16, 19, 51): #South Campus, Yahentamitsi Dining Hall, 251 North id numbers
        location_url = "?locationNum=" + str(i)
        for j in range(delta.days + 1):
            date = start_date + datetime.timedelta(days=j)
            date_url = "&dtdate=" + date.strftime('%m/%d/%Y') # Need to check if there is formatting issue 02 vs 2 for month display
            full_url = url + location_url + date_url
            urls_to_scrape.append(full_url)'''
    urls_to_scrape.append(url + "?locationNum=16&dtdate=02/10/2026") #test case
    scrape(urls_to_scrape)

def scrape(urls_to_scrape):
    for url in urls_to_scrape:
        response = requests.get(url)

        

        time.sleep(1) # Throttle requests to avoid being blocked

if __name__ == '__main__':
    main()