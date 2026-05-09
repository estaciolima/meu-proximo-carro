from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from meu_proximo_carro.mobiauto import collect_listing_urls, crawl_listing
from meu_proximo_carro.paths import RAW_DATA_DIR
from meu_proximo_carro.pipeline import DEFAULT_SEARCH_URL


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl a small Mobiauto search result sample.")
    parser.add_argument("--search-url", default=DEFAULT_SEARCH_URL)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--output")
    args = parser.parse_args()

    urls = collect_listing_urls(args.search_url, limit=args.limit)
    rows = []
    for url in urls:
        try:
            rows.append(crawl_listing(url).to_dict())
        except Exception as exc:
            print(f"Skipping {url}: {exc}")

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    output = Path(args.output) if args.output else RAW_DATA_DIR / f"mobiauto-sample-{int(time.time())}.csv"
    pd.DataFrame(rows).to_csv(output, index=False)
    print(f"Saved {len(rows)} listings to {output}")


if __name__ == "__main__":
    main()
