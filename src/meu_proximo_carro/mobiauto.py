from __future__ import annotations

import json
import re
import time
from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.mobiauto.com.br"
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


@dataclass(frozen=True)
class MobiautoListing:
    url: str
    listing_id: str | None
    fabricante: str | None
    modelo: str | None
    versao: str | None
    modelo_fipe: str | None
    valor: int | None
    valor_fipe: int | None
    cidade: str | None
    ano: str | None
    ano_fabricacao: int | None
    ano_modelo: int | None
    combustivel: str | None
    km: int | None
    cambio: str | None
    cor: str | None
    carroceria: str | None
    features: list[str]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["features"] = json.dumps(self.features, ensure_ascii=False)
        return data


def fetch_html(url: str, timeout: int = 30, session: requests.Session | None = None) -> str:
    client = session or requests.Session()
    response = client.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    response.raise_for_status()
    return response.text


def collect_listing_urls(
    search_url: str,
    *,
    limit: int = 10,
    delay_seconds: float = 0.0,
    session: requests.Session | None = None,
) -> list[str]:
    html = fetch_html(search_url, session=session)
    urls = parse_listing_urls(html, base_url=BASE_URL)
    if delay_seconds:
        time.sleep(delay_seconds)
    return urls[:limit]


def parse_listing_urls(html: str, base_url: str = BASE_URL) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    seen: set[str] = set()
    urls: list[str] = []

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        if "/detalhes/" not in href:
            continue
        url = urljoin(base_url, href)
        if url not in seen:
            seen.add(url)
            urls.append(url)

    return urls


def crawl_listing(url: str, session: requests.Session | None = None) -> MobiautoListing:
    html = fetch_html(url, session=session)
    return parse_listing_page(html, url=url)


def parse_listing_page(html: str, url: str) -> MobiautoListing:
    soup = BeautifulSoup(html, "html.parser")
    next_data = _extract_next_data(soup)
    deal = _find_deal(next_data)

    if deal:
        return _parse_deal_payload(deal, url)

    return _parse_html_fallback(soup, url)


def _extract_next_data(soup: BeautifulSoup) -> dict[str, Any]:
    script = soup.find("script", id="__NEXT_DATA__")
    if not script or not script.string:
        return {}

    try:
        return json.loads(script.string)
    except json.JSONDecodeError:
        return {}


def _find_deal(payload: dict[str, Any]) -> dict[str, Any]:
    page_props = payload.get("props", {}).get("pageProps", {})
    deal = page_props.get("deal")
    return deal if isinstance(deal, dict) else {}


def _parse_deal_payload(deal: dict[str, Any], url: str) -> MobiautoListing:
    make = _clean_text(deal.get("makeName"))
    model = _clean_text(deal.get("modelName"))
    trim = _clean_text(deal.get("trimName"))
    production_year = _safe_int(deal.get("productionYear"))
    model_year = _safe_int(deal.get("modelYear"))
    city = _join_location(deal)

    return MobiautoListing(
        url=url,
        listing_id=_to_str(deal.get("id")),
        fabricante=make,
        modelo=model,
        versao=trim,
        modelo_fipe=" ".join(part for part in [model, trim] if part),
        valor=_safe_int(deal.get("price")),
        valor_fipe=_safe_int(deal.get("fipePrice")),
        cidade=city,
        ano=_format_year(production_year, model_year),
        ano_fabricacao=production_year,
        ano_modelo=model_year,
        combustivel=_clean_text(deal.get("fuelName")),
        km=_safe_int(deal.get("km")),
        cambio=_clean_text(deal.get("transmissionName")),
        cor=_clean_text(deal.get("colorName")),
        carroceria=_clean_text(deal.get("bodystyleName")),
        features=_extract_features_from_deal(deal),
    )


def _parse_html_fallback(soup: BeautifulSoup, url: str) -> MobiautoListing:
    page_text = soup.get_text(" ", strip=True)
    title = _clean_text(soup.find("h1").get_text(" ", strip=True) if soup.find("h1") else None)
    price = _parse_brl(page_text)
    km = _parse_km(page_text)
    listing_id = _extract_listing_id(url)

    make = None
    model = None
    if title:
        title_parts = title.split()
        make = title_parts[0] if title_parts else None
        model = " ".join(title_parts[1:]) if len(title_parts) > 1 else None

    return MobiautoListing(
        url=url,
        listing_id=listing_id,
        fabricante=make,
        modelo=model,
        versao=None,
        modelo_fipe=title,
        valor=price,
        valor_fipe=None,
        cidade=None,
        ano=None,
        ano_fabricacao=None,
        ano_modelo=None,
        combustivel=None,
        km=km,
        cambio=None,
        cor=None,
        carroceria=None,
        features=[],
    )


def _extract_features_from_deal(deal: dict[str, Any]) -> list[str]:
    candidates: list[Any] = []
    for key in ("features", "optionals", "accessories", "items"):
        value = deal.get(key)
        if isinstance(value, list):
            candidates.extend(value)

    features: list[str] = []
    for item in candidates:
        if isinstance(item, str):
            label = item
        elif isinstance(item, dict):
            label = item.get("name") or item.get("label") or item.get("description")
        else:
            label = None
        label = _clean_text(label)
        if label and label not in features:
            features.append(label)

    return features


def _join_location(deal: dict[str, Any]) -> str | None:
    city = _clean_text(deal.get("cityName"))
    state = _clean_text(deal.get("stateAbbreviation") or deal.get("stateName"))
    if city and state:
        return f"{city} - {state}"
    return city or state


def _format_year(production_year: int | None, model_year: int | None) -> str | None:
    if production_year and model_year:
        return f"{production_year}/{model_year}"
    if model_year:
        return str(model_year)
    return None


def _parse_brl(text: str) -> int | None:
    match = re.search(r"R\$\s*([\d.]+)", text)
    if not match:
        return None
    return _safe_int(match.group(1).replace(".", ""))


def _parse_km(text: str) -> int | None:
    match = re.search(r"([\d.]+)\s*km", text, flags=re.IGNORECASE)
    if not match:
        return None
    return _safe_int(match.group(1).replace(".", ""))


def _extract_listing_id(url: str) -> str | None:
    match = re.search(r"/detalhes/(\d+)", url)
    return match.group(1) if match else None


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _safe_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(str(value).replace(".", "").replace(",", ".")))
    except (TypeError, ValueError):
        return None


def _to_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)
