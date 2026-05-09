import os
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from meu_proximo_carro.fipe import get_marcas
from meu_proximo_carro.mobiauto import collect_listing_urls, crawl_listing
from meu_proximo_carro.pipeline import DEFAULT_SEARCH_URL


RUN_LIVE = os.getenv("RUN_LIVE_CRAWLER_TESTS") == "1"


@unittest.skipUnless(RUN_LIVE, "Set RUN_LIVE_CRAWLER_TESTS=1 to run live crawler checks.")
class LiveCrawlerSmokeTest(unittest.TestCase):
    def test_mobiauto_live_sample_has_required_fields(self):
        urls = collect_listing_urls(DEFAULT_SEARCH_URL, limit=1)
        self.assertTrue(urls)

        listing = crawl_listing(urls[0])

        self.assertTrue(listing.listing_id)
        self.assertTrue(listing.fabricante)
        self.assertTrue(listing.modelo)
        self.assertIsInstance(listing.valor, int)
        self.assertGreater(listing.valor, 0)

    def test_fipe_live_marcas_returns_fiat(self):
        marcas = get_marcas()

        self.assertTrue(any(item["Label"].lower() == "fiat" for item in marcas))


if __name__ == "__main__":
    unittest.main()

