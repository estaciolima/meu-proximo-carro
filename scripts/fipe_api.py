import pandas as pd
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from meu_proximo_carro import fipe as _fipe

def consulta_fipe(codigo_marca : str, codigo_modelo : str, codigo_ano : str, tabela_ref=None):
    return _fipe.consulta_fipe(codigo_marca, codigo_modelo, codigo_ano, tabela_ref or _fipe.get_latest_tabela_ref())

def get_codigo_marcas(tabela_ref=None):
    '''
        Retornar lista com codigo de marcas.
    '''
    class _Response:
        status_code = 200

        def __init__(self, data):
            self._data = data
            self.text = pd.DataFrame(data).to_json(orient="records")

        def json(self):
            return self._data

    return _Response(_fipe.get_marcas(tabela_ref or _fipe.get_latest_tabela_ref()))

def get_codigo_modelo(codigo_marca):
    '''
        Retorna lista com codigos de modelos da marca consultada.
    '''
    class _Response:
        status_code = 200

        def __init__(self, data):
            self._data = {"Modelos": data}

        def json(self):
            return self._data

    return _Response(_fipe.get_modelos(codigo_marca))

def get_codigo_ano(codigo_marca, codigo_modelo):
    '''
        Retornar lista de ano e modelos do veiculo
    '''
    class _Response:
        status_code = 200

        def __init__(self, data):
            self._data = data
            self.text = pd.DataFrame(data).to_json(orient="records")

        def json(self):
            return self._data

    return _Response(_fipe.get_anos(codigo_marca, codigo_modelo))

def consultar_historico_modelo(codigo_marca, codigo_modelo, codigo_ano, tabela_ref=None):
    '''
        Criar histórico de preços, como o preço mais recente estando na 'tabela_ref', até a entrada mais antiga.
    '''
    prices = _fipe.consultar_historico_modelo(
        str(codigo_marca),
        str(codigo_modelo),
        str(codigo_ano),
        str(tabela_ref or _fipe.get_latest_tabela_ref()),
        months=24,
        sleep_seconds=2,
    )
    return pd.DataFrame([price.to_dict() for price in prices])
