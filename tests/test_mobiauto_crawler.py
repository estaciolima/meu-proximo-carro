import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from meu_proximo_carro.mobiauto import parse_listing_page, parse_listing_urls


class MobiautoCrawlerTest(unittest.TestCase):
    def test_parse_listing_urls_deduplicates_detail_links(self):
        html = """
        <a href="/comprar/carros/sp/modelo/detalhes/123?page=detail">A</a>
        <a href="https://www.mobiauto.com.br/comprar/carros/sp/modelo/detalhes/123?page=detail">A</a>
        <a href="/comprar/carros/sp/modelo/detalhes/456?page=detail">B</a>
        """

        urls = parse_listing_urls(html)

        self.assertEqual(
            urls,
            [
                "https://www.mobiauto.com.br/comprar/carros/sp/modelo/detalhes/123?page=detail",
                "https://www.mobiauto.com.br/comprar/carros/sp/modelo/detalhes/456?page=detail",
            ],
        )

    def test_parse_listing_page_from_next_data_payload(self):
        payload = {
            "props": {
                "pageProps": {
                    "deal": {
                        "id": 27973582,
                        "makeName": "GWM",
                        "modelName": "Ora 03",
                        "trimName": "GT",
                        "price": 147900,
                        "fipePrice": 145077,
                        "cityName": "Guarulhos",
                        "stateAbbreviation": "SP",
                        "productionYear": 2023,
                        "modelYear": 2024,
                        "fuelName": "Eletricidade",
                        "km": 50000,
                        "transmissionName": "Automatica",
                        "colorName": "Branco",
                        "bodystyleName": "Hatch",
                        "features": [{"name": "Camera de re"}, {"name": "Teto solar"}],
                    }
                }
            }
        }
        html = f'<html><script id="__NEXT_DATA__" type="application/json">{json.dumps(payload)}</script></html>'

        listing = parse_listing_page(
            html,
            url="https://www.mobiauto.com.br/comprar/carros/sp-guarulhos/gwm/ora-03/2024/gt/detalhes/27973582?page=detail",
        )

        self.assertEqual(listing.listing_id, "27973582")
        self.assertEqual(listing.fabricante, "GWM")
        self.assertEqual(listing.modelo, "Ora 03")
        self.assertEqual(listing.versao, "GT")
        self.assertEqual(listing.valor, 147900)
        self.assertEqual(listing.valor_fipe, 145077)
        self.assertEqual(listing.cidade, "Guarulhos - SP")
        self.assertEqual(listing.ano, "2023/2024")
        self.assertEqual(listing.km, 50000)
        self.assertEqual(listing.features, ["Camera de re", "Teto solar"])


if __name__ == "__main__":
    unittest.main()
