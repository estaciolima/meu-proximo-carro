from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

url = "https://www.mobiauto.com.br/comprar/carros/ba-paulo-afonso/volkswagen/virtus/2023/1-0-200-tsi-highline-flex-aut/detalhes/7320664?page=detail&utm_medium=cpc&utm_source=google&utm_date=1701045556082&utm_term=Search_Institucional_BR,performance_mobiauto&gclid=CjwKCAiA9ourBhAVEiwA3L5RFpyf6vWm5J9ErRfBeuj1iY4gH5AwDxBR0rTYPeCyORpMw1MvuF6MDRoCaXUQAvD_BwE"

def car_crawler(url):
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'})
    html = urlopen(request)
    bs = BeautifulSoup(html.read(), 'html.parser')

    ficha_tecnica = {}

    ficha_tecnica['Fabricante'] = bs.find('span', {'class': 'mui-style-z7se3t'}).get_text()
    ficha_tecnica['Modelo'] = bs.find('span', {'class': 'mui-style-187svjm'}).get_text()
    ficha_tecnica['Versao'] = bs.find('h2', {'class': 'mui-style-hka4fm'}).get_text()
    ficha_tecnica['Valor'] = bs.find('p', {'class': 'mui-style-gzbtep'}).get_text()

    general_header = bs.find_all('p', {'class': 'mui-style-1nwyav9'})
    general_info = bs.find_all('div', {'class': 'mui-style-1mzljxq'})

    # TODO nao está pegando a info do câmbio
    for header,info in zip(general_header, general_info):
        print(f'{header.get_text()}: {info.get_text()}')
        ficha_tecnica[header.get_text()] = info.get_text()

    features = bs.find_all('div', {'class': 'mui-style-av0skd'})

    for feature in features:
        print(f'feature: {feature.get_text()}')
        ficha_tecnica[feature.get_text()] = "Sim"

    tech_specs = bs.find_all('div', {'class': 'mui-style-7cwry4'})

    for tech_spec in tech_specs:
        if (len(tech_spec.contents) == 3):
            print(f'{tech_spec.contents[0].get_text()}: {tech_spec.contents[2].get_text()}')
            ficha_tecnica[tech_spec.contents[0].get_text()] = tech_spec.contents[2].get_text()
        else:
            print(f'tech spec: {tech_spec.get_text()}')
            ficha_tecnica[tech_spec.get_text()] = 'Sim'

    return ficha_tecnica

# https://stackoverflow.com/questions/28097222/pandas-merge-two-dataframes-with-different-columns