from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

def car_crawler(url):
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'})
    html = urlopen(request)
    bs = BeautifulSoup(html.read(), 'html.parser')

    print(f'URL being scraped: {url}')

    ficha_tecnica = {}
    ficha_tecnica['URL'] = url

    try:
        ficha_tecnica['Fabricante'] = [bs.find('span', {'class': 'css-z7se3t'}).get_text()]
    except AttributeError:
        print('Veículo não está mais disponível!')
        return {}
    
    ficha_tecnica['Modelo'] = [bs.find('span', {'class': 'css-1gr8pbn'}).get_text()]
    ficha_tecnica['Versao'] = [bs.find('h2', {'class': 'css-hf0294'}).get_text()]
    ficha_tecnica['Valor'] = [bs.find('p', {'class': 'css-h31tor'}).get_text()]

    general_header = bs.find_all('p', {'class': 'css-1nwyav9'})
    general_info = bs.find_all('div', {'class': 'css-1mzljxq'})

    # TODO nao está pegando a info do câmbio
    for header,info in zip(general_header, general_info):
        #print(f'{header.get_text()}: {info.get_text()}')
        ficha_tecnica[header.get_text()] = [info.get_text()]

    features = bs.find_all('div', {'class': 'css-av0skd'})

    for feature in features:
        #print(f'feature: {feature.get_text()}')
        ficha_tecnica[feature.get_text()] = ["Sim"]

    tech_specs = bs.find_all('div', {'class': 'css-7cwry4'})

    for tech_spec in tech_specs:
        if (len(tech_spec.contents) == 3):
            #print(f'{tech_spec.contents[0].get_text()}: {tech_spec.contents[2].get_text()}')
            chave =  tech_spec.contents[0].get_text()
            valor = tech_spec.contents[2].get_text()
            if(chave not in ficha_tecnica):
                ficha_tecnica[chave] = [valor]
        else:
            #print(f'tech spec: {tech_spec.get_text()}')
            chave = tech_spec.get_text()
            if (chave not in ficha_tecnica):
                ficha_tecnica[chave] = ['Sim']

    return ficha_tecnica