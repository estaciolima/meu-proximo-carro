import requests
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import pandas as pd

def consulta_fipe(codigo_marca : str, codigo_modelo : str, codigo_ano : str, tabela_ref='306'):
    codigo_ano = codigo_ano.split('-') # o ano na interface da FIPE é fornecido no formato '2011-1', em que 2011 é o ano e 1 é o tipo de combustível
    ano = codigo_ano[0] 
    tipo_combustivel = codigo_ano[1]

    payload = {
        'codigoTabelaReferencia': tabela_ref,
        'codigoMarca': codigo_marca,
        'codigoModelo': codigo_modelo,
        'codigoTipoVeiculo': '1',
        'anoModelo': ano,
        'codigoTipoCombustivel': tipo_combustivel,
        'tipoVeiculo': 'carro',
        'modeloCodigoExterno': '' ,
        'tipoConsulta': 'tradicional'
    }

    r = requests.post('https://veiculos.fipe.org.br/api/veiculos//ConsultarValorComTodosParametros', json=payload)

    print(f'response status code: {r.status_code}')

    # TODO: site retorna {'codigo': '0', 'erro': 'nadaencontrado'} quando nao encontra dados, checar isso no futuro

    return r.json()

def get_codigo_marcas(tabela_ref='306'):
    '''
        Retornar lista com codigo de marcas.
    '''
    payload = {
        'codigoTabelaReferencia': tabela_ref,
        'codigoTipoVeiculo': '1'
    }

    r = requests.post('https://veiculos.fipe.org.br/api/veiculos//ConsultarMarcas', json=payload)

    print(f'response status code: {r.status_code}')

    return r

def get_codigo_modelo(codigo_marca):
    '''
        Retorna lista com codigos de modelos da marca consultada.
    '''
    payload = {
        'codigoTabelaReferencia': '306',
        'codigoTipoVeiculo': '1',
        'codigoMarca': codigo_marca
    }

    r = requests.post('https://veiculos.fipe.org.br/api/veiculos//ConsultarModelos', json=payload)
    
    print(f'response status code: {r.status_code}')

    return r

def get_codigo_ano(codigo_marca, codigo_modelo):
    '''
        Retornar lista de ano e modelos do veiculo
    '''
    payload = {
        'codigoTabelaReferencia': '306',
        'codigoTipoVeiculo': '1',
        'codigoModelo': codigo_modelo,
        'codigoMarca': codigo_marca
    }

    r = requests.post('https://veiculos.fipe.org.br/api/veiculos//ConsultarAnoModelo', json=payload)
    
    print(f'response status code: {r.status_code}')

    return r

def guardar_codigo_marcas(tabela_ref='306'):
    '''
        Cria um csv com todos os códigos de marcas usados pela FIPE.
    '''
    lista_de_codigos = get_codigo_marcas(tabela_ref)
    df = pd.read_json(lista_de_codigos.text)
    df.to_csv('lista_de_codigos_de_marcas.csv', index=False)
    print('File created!')

def guardar_modelos(codigo_marca):
    '''
        Baixa lista de modelos de uma marca.
    '''
    resposta = get_codigo_modelo(codigo_marca)
    df = pd.DataFrame.from_records(resposta.json()['Modelos'])
    df.to_csv('lista_de_modelos_21.csv', index=False)

def guardar_anos(codigo_marca, codigo_modelo):
    resposta = get_codigo_ano(codigo_marca, codigo_modelo)
    df = pd.read_json(resposta.text)
    df.to_csv('lista_de_anos_21_5273.csv', index=False)


guardar_anos('21', '5273')

