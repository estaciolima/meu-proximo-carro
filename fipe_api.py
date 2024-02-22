import requests
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

def consulta_fipe(marca : str, modelo : str, ano : str):
    payload = {
        'codigoTabelaReferencia': '306',
        'codigoMarca': marca,
        'codigoModelo': modelo,
        'codigoTipoVeiculo': '1',
        'anoModelo': ano,
        'codigoTipoCombustivel': '1',
        'tipoVeiculo': 'carro',
        'modeloCodigoExterno': '' ,
        'tipoConsulta': 'tradicional'
    }

    r = requests.post('https://veiculos.fipe.org.br/api/veiculos//ConsultarValorComTodosParametros', json=payload)

    print(f'response status code: {r.status_code}')

    return r.json()

def return_codigo_marcas():
    '''
        Retornar lista com codigo de marcas
    '''
    payload = {
        'codigoTabelaReferencia': '306',
        'codigoTipoVeiculo': '1'
    }

    r = requests.post('https://veiculos.fipe.org.br/api/veiculos//ConsultarMarcas', json=payload)

    print(f'response status code: {r.status_code}')

    return r.json()
