import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from meu_proximo_carro.fipe import parse_brl, parse_price_response, post_fipe


class FakeResponse:
    status_code = 200

    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self):
        self.calls = []

    def post(self, url, json, headers, timeout):
        self.calls.append({"url": url, "json": json, "headers": headers, "timeout": timeout})
        return FakeResponse([{"Label": "Fiat", "Value": "21"}])


class FipeApiTest(unittest.TestCase):
    def test_parse_brl(self):
        self.assertEqual(parse_brl("R$ 12.345,00"), 12345)
        self.assertIsNone(parse_brl(None))

    def test_parse_price_response(self):
        price = parse_price_response(
            {
                "Marca": "Fiat",
                "Modelo": "147 C/ CL",
                "AnoModelo": 1987,
                "Combustivel": "Gasolina",
                "CodigoFipe": "001001-1",
                "MesReferencia": "maio de 2026",
                "Valor": "R$ 8.500,00",
            }
        )

        self.assertEqual(price.marca, "Fiat")
        self.assertEqual(price.valor, 8500)
        self.assertEqual(price.codigo_fipe, "001001-1")

    def test_post_fipe_uses_browser_headers(self):
        session = FakeSession()

        result = post_fipe("ConsultarMarcas", {"codigoTipoVeiculo": "1"}, session=session)

        self.assertEqual(result, [{"Label": "Fiat", "Value": "21"}])
        self.assertIn("veiculos.fipe.org.br", session.calls[0]["url"])
        self.assertEqual(session.calls[0]["headers"]["Origin"], "https://veiculos.fipe.org.br")
        self.assertIn("Mozilla", session.calls[0]["headers"]["User-Agent"])


if __name__ == "__main__":
    unittest.main()

