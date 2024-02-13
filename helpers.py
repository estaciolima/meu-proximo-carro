import unidecode

def collect_car_pages(bs):
    '''
    This function returns a list 'car_pages' with the links for the car pages to be used as argument to the car_crawler() function later on.
    
    Arguments: 
        - bs -> BeutifulSoup object
    '''
    pages_links = bs.findAll('div', {'class':'active mui-style-14y9di7'})
    car_pages = []

    for pages in pages_links:
        car_page = pages.a.get("href")
        car_pages.append(car_page)

    return car_pages


def convert_valor_to_numerical(valor):
    valor = unidecode.unidecode(valor) # convert '\xa' to ASCII
    valor = valor.replace('.','') # remove '.' value separator from string
    valor = valor.split()

    if len(valor) == 1:
        return int(valor[0])
    elif len(valor) == 2:
        return int(valor[1])
    else:
        raise Exception('More fields than expected: {}'.format(valor))