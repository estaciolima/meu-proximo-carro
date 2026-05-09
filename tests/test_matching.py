import sys
import unittest
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from meu_proximo_carro.matching import find_similar_fipe_model, normalize_vehicle_name


class MatchingTest(unittest.TestCase):
    def test_normalize_vehicle_name_removes_accents_and_fuel_noise(self):
        self.assertEqual(
            normalize_vehicle_name("Câmbio Automático 1.0 Flex"),
            "cambio automatico 1 0",
        )

    def test_find_similar_fipe_model_by_brand_and_year(self):
        candidates = pd.DataFrame(
            [
                {"Marca": "Volkswagen", "Modelo": "T-Cross 1.0 200 TSI Comfortline (Aut) (Flex)", "Ano": 2022},
                {"Marca": "Volkswagen", "Modelo": "Gol 1.0", "Ano": 2022},
                {"Marca": "Fiat", "Modelo": "Fastback Impetus Turbo 200", "Ano": 2023},
            ]
        )

        match = find_similar_fipe_model(
            "T Cross Comfortline 200 TSI automatico",
            "Volkswagen",
            candidates,
            model_year=2022,
            year_column="Ano",
        )

        self.assertEqual(match.value, "T-Cross 1.0 200 TSI Comfortline (Aut) (Flex)")
        self.assertGreaterEqual(match.score, 70)


if __name__ == "__main__":
    unittest.main()
