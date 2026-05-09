import pandas as pd
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from meu_proximo_carro.mobiauto import crawl_listing as _crawl_listing
from meu_proximo_carro.matching import find_similar_fipe_model

def _find_similar_models(model_name:str, model_oem:str) -> str:
    '''
    Find the closest FIPE model name using lightweight fuzzy matching.
    '''
    df = pd.read_csv(PROJECT_ROOT / "data" / "lookup" / "nomes_fipe.csv")
    match = find_similar_fipe_model(model_name, model_oem, df)
    return match.value

def car_crawler(url):
    return _crawl_listing(url).to_dict()
