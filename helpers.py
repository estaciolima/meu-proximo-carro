import unidecode
import pandas as pd

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
    
def data_preparation(df: pd.DataFrame) -> pd.DataFrame:
    '''
        Cleate new variables and treat missing values
    '''
    df = df.copy()
    # Drop duplicates
    df.drop_duplicates(inplace=True)

    # Create columns 'Production year' and 'Model year'
    df['Production year'] = df['Ano'].apply(lambda x: int(str.split(x, '/')[0]))
    df['Model year'] = df['Ano'].apply(lambda x: int(str.split(x, '/')[1]))

    # Create vehicle identifier based on model, version and model year
    identificador_unico = []
    for ano, modelo, versao in zip(df['Model year'], df['Modelo'], df['Versao']):
        identificador_unico.append('{}-{}-{}'.format(ano, modelo, versao))

    df['Carro ID'] = identificador_unico

    # Identify rows with the same vehicle identifier and fill missing values with the column most common value.
    # Reasoning is that since the car announcement is manually created by the customer, missing information is likely.
    for carro_id in df['Carro ID']:
        mask = df['Carro ID'] == carro_id
        columns = df.columns.tolist()
        to_fillna = dict(zip(columns, df[mask].mode().loc[0,:].values.tolist()))
        df[mask] = df[mask].fillna(to_fillna)

    # Then, assume that in case any missing values remain, it means that vehicle does not have this feature.
    df.fillna('Não', inplace=True) 

    # Convert column 'Valor' from object (string) to numerical (int)
    df['Valor'] = df['Valor'].apply(convert_valor_to_numerical)

    # Convert column 'KM' from object (string) to numerical (int)
    df['KM'] = df['KM'].apply(lambda x: int(x.replace('.','')))

    # Drop useless columns
    df.drop(['Unnamed: 0', 'URL', 'Placa final', 'Ano', 'Carro ID', 'Production year'], axis=1, inplace=True)

    # Dataset contains absurd KM values that breaks some analysis, I remove them here:
    df.drop(df[df['KM'] > 1000000].index, inplace=True)

    return df