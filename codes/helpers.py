import unidecode
import pandas as pd

# This code is used to scrape car data from a website and prepare the data for analysis.
def collect_car_pages(bs):
    '''
    This function returns a list 'car_pages' with the links for the car pages to be used as argument to the car_crawler() function later on.
    
    Arguments: 
        - bs -> BeutifulSoup object
    '''
    pages_links = bs.findAll('div', {'class':'active css-14y9di7'})
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
        Cleate new variables and treat missing values.
        Prepare the database to start the analysis.
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

    # df['Carro ID'] = identificador_unico

    # Identify rows with the same vehicle identifier and fill missing values with the column most common value.
    # Reasoning is that since the car announcement is manually created by the customer, missing information is likely.
    # for carro_id in df['Carro ID']:
    #     mask = df['Carro ID'] == carro_id
    #     columns = df.columns.tolist()
    #     to_fillna = dict(zip(columns, df[mask].mode().loc[0,:].values.tolist()))
    #     df[mask] = df[mask].fillna(to_fillna)

    # Then, assume that in case any missing values remain, it means that vehicle does not have this feature.
    df.fillna('Não', inplace=True) 

    # Convert column 'Valor' from object (string) to numerical (int)
    df['Valor'] = df['Valor'].apply(convert_valor_to_numerical)

    # Convert column 'KM' from object (string) to numerical (int)
    #df['KM'] = df['KM'].apply(lambda x: int(x.replace('.','')))

    # Drop useless columns
    # df.drop(['Unnamed: 0', 'URL', 'Placa final', 
    #          'Ano', 'Carro ID', 'Production year',
    #          'Câmbio automático'], axis=1, inplace=True)

    # Dataset contains absurd KM values that breaks some analysis, I remove them here:
    df.drop(df[df['KM'] > 1000000].index, inplace=True)

    return df

# This code is used to generate and load embeddings for car model names using the SentenceTransformer model.
from sentence_transformers import SentenceTransformer, util
import torch

def generate_embeddings():
    '''
    This function generates the embeddings for the car model names and saves them in a pickle file.
    The embeddings are generated using the SentenceTransformer model 'all-MiniLM-L6-v2'.
    The embeddings are saved in the '../embeddings/embeddings.pkl' file.
    The embeddings are generated for the car model names in the '../datasets/database-dashboard.csv' file.
    '''
    # Load the model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Load the dataset
    df = pd.read_csv('../datasets/database-dashboard.csv')
    df = df[['Modelo_FIPE', 'Fabricante', 'Model year']]
    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Car names
    model_names = df['Modelo_FIPE']

    # Generate the embeddings
    embeddings = model.encode(model_names, convert_to_tensor=True)

    # Save as parquet
    df['embedding'] = [embeddings[i].tolist() for i in range(len(embeddings))]
    df.to_parquet("../embeddings/embeddings.parquet", index=False)

    print('Embeddings saved in /embeddings/embeddings.parquet')

def load_embeddings():
    '''
    This function loads the embeddings from the parquet file.
    '''
    try:
        print('Loading embeddings...')
        df = pd.read_parquet("../embeddings/embeddings.parquet")
    except FileNotFoundError:
        print('File not found. Generating embeddings...')
        generate_embeddings()
        print('Embeddings generated.')
        print('Loading embeddings again...')
        df = pd.read_parquet("../embeddings/embeddings.parquet")

    df["embedding"] = df["embedding"].apply(lambda x: torch.tensor(x))

    return df

def find_similar_models(model_name:str, model_oem:str, model_year:int) -> str:
    '''
    This function finds the most similar car models to the given model name.
    The function uses the embeddings generated by the SentenceTransformer model 'all-MiniLM-L6-v2'.
    The function returns a list of tuples with the model name and the similarity score.
    '''
    # Load the model
    model = SentenceTransformer('all-MiniLM-L6-v2') # precisa ser o mesmo da função generate_embeddings()

    # Generate the embedding for the given model name
    model_embedding = model.encode(model_name, convert_to_tensor=True)

    # Load the embeddings
    df = load_embeddings()

    df = df[(df['Fabricante'] == model_oem) &
                     (df['Model year'] == model_year)]

    model_names = df['Modelo_FIPE'].tolist()
    embeddings = df['embedding'].tolist()

    # Calcular similaridade
    similaridades = util.cos_sim(model_embedding, embeddings)

    # Indice do texto mais similar
    indice = torch.argmax(similaridades)
    return model_names[indice]