
from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup


#driver = webdriver.Firefox()
url = "https://www.mobiauto.com.br/comprar/carros/mg-uberlandia/fiat/pulse/2022/drive-200-turbo-flex-aut/detalhes/9384139?page=detail&utm_campaign=Search_Institucional_BR&utm_medium=cpc&utm_source=google&utm_date=1701045556082&utm_term=Search_Institucional_BR,performance_mobiauto&gclid=CjwKCAiA9ourBhAVEiwA3L5RFpyf6vWm5J9ErRfBeuj1iY4gH5AwDxBR0rTYPeCyORpMw1MvuF6MDRoCaXUQAvD_BwE"
request = Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'})
html = urlopen(request)
bs = BeautifulSoup(html.read(), 'html.parser')

brand = bs.find('span', {'class': 'mui-style-z7se3t'})

print(brand.get_text())

#driver.get(url)
#title = driver.find_element(By.ID, 'title')
#print(f'Title: {title.text}')