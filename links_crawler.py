from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from helpers import collect_car_pages
import time
import pandas as pd
from car_crawler import car_crawler

start_time = time.time()

base_url = "https://www.mobiauto.com.br"
url = "https://www.mobiauto.com.br/comprar/carros/ba-salvador?utm_medium=cpc&utm_source=google&utm_date=1701045556082&utm_term=Search_Institucional_BR,performance_mobiauto&gclid=CjwKCAiA9ourBhAVEiwA3L5RFpyf6vWm5J9ErRfBeuj1iY4gH5AwDxBR0rTYPeCyORpMw1MvuF6MDRoCaXUQAvD_BwE"

request = Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'})
html = urlopen(request)
bs = BeautifulSoup(html, 'html.parser')

next_page_link = bs.find('span', {'aria-label': 'Ir para próxima página'}).parent.get('href')
car_pages = collect_car_pages(bs)

count = 1

while(next_page_link != None):
    print(f'Scraping page {count}...')
    url = base_url + next_page_link
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'})
    html = urlopen(request)
    bs = BeautifulSoup(html, 'html.parser')
    car_pages.extend(collect_car_pages(bs))
    try:
        next_page_link = bs.find('span', {'aria-label': 'Ir para próxima página'}).parent.get('href')   
    except AttributeError:
        next_page_link = None
    count += 1
    break # debugging purpose - delete after

get_all_the_links_time = time.time()
print(f'Time to get all the links: {get_all_the_links_time-start_time}') # ~2 min

df = pd.DataFrame()

for url in car_pages:
    car_info = car_crawler(url)
    car_info = pd.DataFrame(car_info)
    df = pd.concat([df,car_info], ignore_index=True)

df.to_csv(f'database-{time.time()}.csv')

print(f'Time to scrap all the pages: {time.time()-get_all_the_links_time}') # ~ 32 min