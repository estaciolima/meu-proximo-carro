import requests
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import pandas as pd
import time
import random
import time

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

def get_codigo_marcas(tabela_ref='320'):
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
        'codigoTabelaReferencia': '320',
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
        'codigoTabelaReferencia': '320',
        'codigoTipoVeiculo': '1',
        'codigoModelo': codigo_modelo,
        'codigoMarca': codigo_marca
    }

    r = requests.post('https://veiculos.fipe.org.br/api/veiculos//ConsultarAnoModelo', json=payload)
    
    print(f'response status code: {r.status_code}')

    return r

def guardar_codigo_marcas(tabela_ref='320'):
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
    df.to_csv(f'lista_de_modelos_{codigo_marca}.csv', index=False)

def guardar_anos(codigo_marca, codigo_modelo):
    '''
        Baixa lista de anos modelo de um modelo de uma marca.
    '''
    resposta = get_codigo_ano(codigo_marca, codigo_modelo)
    df = pd.read_json(resposta.text)
    df.to_csv(f'lista_de_anos_{codigo_marca}_{codigo_modelo}.csv', index=False)

def consultar_historico_modelo(codigo_marca, codigo_modelo, codigo_ano, tabela_ref):
    '''
        Criar histórico de preços, como o preço mais recente estando na 'tabela_ref', até a entrada mais antiga.
    '''
    historico = []

    print(f'tabela ref: {tabela_ref}')
    resposta = consulta_fipe(codigo_marca, codigo_modelo, codigo_ano, tabela_ref)

    while ('codigo' not in resposta.keys()):
        tabela_ref = str(int(tabela_ref)-1)
        print(f'tabela ref: {tabela_ref}')
        historico.append(resposta)
        resposta = consulta_fipe(codigo_marca, codigo_modelo, codigo_ano, tabela_ref)
        time.sleep(2+random.random())


    df = pd.DataFrame.from_records(historico)
    return df

def criar_dataset_com_modelos_e_marcas():
    '''
        Objetivo é gerar um arquivo CSV com todos os modelos de todas as marcas disponíveis na Tabela FIPE.
        A partir disso, criar um dashboard em que o usuário vai poder selecionar Marca>Modelo>Ano.
    '''
    try:
        lista_de_marcas = pd.read_csv('lista_de_codigos_de_marcas.csv')
    except FileNotFoundError:
        # a principio nao vou programar nada, depois ajusto com mais maturidade sobre o que realmente preciso
        print("Arquivo nao existe!")
        return 0
    
    lista_completa = []
    

    for linha in lista_de_marcas.iloc[21:23].itertuples(): # TODO: remover o iloc depois que confirmar que codigo funciona
        print(f'Carregando modelos da marca: {linha.Label}')
        resposta_api = get_codigo_modelo(linha.Value)
        
        tentativa = 1

        # existe uma restrição de número de requisições em um determinado tempo:
        while(resposta_api.status_code != 200):
            tempo_espera = 2 ** tentativa  # espera exponencial: 2, 4, 8, 16, ...
            print(f"429 recebido. Tentando novamente em {tempo_espera} segundos...")
            tentativa += 1
            time.sleep(tempo_espera)
            resposta_api = get_codigo_modelo(linha.Value)

        modelos = resposta_api.json()

        if 'erro' in modelos.keys():
            continue

        for modelo in modelos['Modelos']:
            resposta_api = get_codigo_ano(linha.Value, modelo['Value'])
            print(f'Modelo: {modelo["Label"]}')
            # TODO: ver se tem uma forma melhor de verificar o status code 200, estou repetindo código
            tentativa = 1
            while(resposta_api.status_code != 200):
                tempo_espera = 2 ** tentativa  # espera exponencial: 2, 4, 8, 16, ...
                print(f"429 recebido. Tentando novamente em {tempo_espera} segundos...")
                tentativa += 1
                time.sleep(tempo_espera)
                resposta_api = get_codigo_ano(linha.Value, modelo['Value'])

            anoModelos = resposta_api.json()

            for anoModelo in anoModelos:
                lista_completa.append((linha.Label,
                                       linha.Value,
                                       modelo['Label'],
                                       modelo['Value'],
                                       anoModelo['Label'],
                                       anoModelo['Value']))

    df = pd.DataFrame(lista_completa, columns=['Marca', 'Código Marca', 'Modelo', 'Código Modelo', 'Ano', 'Código Ano'])

    df.to_csv('lista_completa_fiat.csv', index=False)