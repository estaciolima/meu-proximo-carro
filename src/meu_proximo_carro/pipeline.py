from __future__ import annotations

import argparse
from dataclasses import asdict

from . import fipe, mobiauto
from .database import connect_sqlite, init_sqlite_db, upsert_fipe_prices, upsert_listings


DEFAULT_SEARCH_URL = "https://www.mobiauto.com.br/comprar/carro/brasil"


def populate_sample_database(
    *,
    search_url: str = DEFAULT_SEARCH_URL,
    limit: int = 3,
    fipe_months: int = 1,
) -> dict[str, int]:
    connection = connect_sqlite()
    init_sqlite_db(connection)

    urls = mobiauto.collect_listing_urls(search_url, limit=limit)
    listings = []
    for url in urls:
        try:
            listings.append(mobiauto.crawl_listing(url).to_dict())
        except Exception as exc:
            print(f"Skipping Mobiauto listing {url}: {exc}")

    inserted_listings = upsert_listings(connection, listings)

    # Small deterministic FIPE sample: Fiat 147 C/CL 1987 Gasolina.
    tabela_ref = fipe.get_latest_tabela_ref()
    prices = fipe.consultar_historico_modelo(
        codigo_marca="21",
        codigo_modelo="437",
        codigo_ano="1987-1",
        tabela_ref=tabela_ref,
        months=fipe_months,
    )
    inserted_prices = upsert_fipe_prices(connection, [asdict(price) for price in prices])

    return {"mobiauto_listings": inserted_listings, "fipe_prices": inserted_prices}


def main() -> None:
    parser = argparse.ArgumentParser(description="Populate a small local sample database.")
    parser.add_argument("--search-url", default=DEFAULT_SEARCH_URL)
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--fipe-months", type=int, default=1)
    args = parser.parse_args()

    result = populate_sample_database(
        search_url=args.search_url,
        limit=args.limit,
        fipe_months=args.fipe_months,
    )
    print(result)


if __name__ == "__main__":
    main()
