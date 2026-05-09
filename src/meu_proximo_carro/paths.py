from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
LOOKUP_DATA_DIR = DATA_DIR / "lookup"
DEFAULT_SQLITE_PATH = PROCESSED_DATA_DIR / "meu_proximo_carro.db"

