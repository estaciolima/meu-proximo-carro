from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from helpers import collect_car_pages
from car_crawler import car_crawler
import time
import pandas as pd

base_url = "https://www.mobiauto.com.br"
url = "https://www.mobiauto.com.br/comprar/carros/ba-salvador?utm_medium=cpc&utm_source=google&utm_date=1701045556082&utm_term=Search_Institucional_BR,performance_mobiauto&gclid=CjwKCAiA9ourBhAVEiwA3L5RFpyf6vWm5J9ErRfBeuj1iY4gH5AwDxBR0rTYPeCyORpMw1MvuF6MDRoCaXUQAvD_BwE"

request = Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'})
html = urlopen(request)
bs = BeautifulSoup(html, 'html.parser')

next_page_link = bs.find('button', {'data-testid': 'next-button'}).parent.get('href')
car_pages = collect_car_pages(bs)

count = 0

while(next_page_link != None):
    url = base_url + next_page_link
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'})
    html = urlopen(request)
    bs = BeautifulSoup(html, 'html.parser')
    car_pages.extend(collect_car_pages(bs))
    next_page_link = bs.find('button', {'data-testid': 'next-button'}).parent.get('href')
    count += 1
    
    if (count > 1):
        # just for initial tests
        break

    time.sleep(3) # looking less like a robot
