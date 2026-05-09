from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from typing import Any

import requests


BASE_URL = "https://veiculos.fipe.org.br/api/veiculos"
DEFAULT_TABLE_REFERENCE = "333"
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    ),
    "Referer": "https://veiculos.fipe.org.br/",
    "Origin": "https://veiculos.fipe.org.br",
    "Content-Type": "application/json",
}


@dataclass(frozen=True)
class FipePrice:
    marca: str | None
    modelo: str | None
    ano_modelo: int | None
    combustivel: str | None
    codigo_fipe: str | None
    mes_referencia: str | None
    valor: int | None
    raw_valor: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def post_fipe(
    endpoint: str,
    payload: dict[str, Any],
    *,
    session: requests.Session | None = None,
    timeout: int = 30,
) -> Any:
    client = session or requests.Session()
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    response = client.post(url, json=payload, headers=DEFAULT_HEADERS, timeout=timeout)
    response.raise_for_status()
    return response.json()


def get_tabelas_referencia(*, session: requests.Session | None = None) -> list[dict[str, Any]]:
    data = post_fipe("ConsultarTabelaDeReferencia", {}, session=session)
    return data if isinstance(data, list) else []


def get_latest_tabela_ref(*, session: requests.Session | None = None) -> str:
    tabelas = get_tabelas_referencia(session=session)
    if not tabelas:
        return DEFAULT_TABLE_REFERENCE
    return str(tabelas[0]["Codigo"])


def get_marcas(
    tabela_ref: str = DEFAULT_TABLE_REFERENCE,
    *,
    session: requests.Session | None = None,
) -> list[dict[str, str]]:
    payload = {"codigoTabelaReferencia": tabela_ref, "codigoTipoVeiculo": "1"}
    return post_fipe("ConsultarMarcas", payload, session=session)


def get_modelos(
    codigo_marca: str,
    tabela_ref: str = DEFAULT_TABLE_REFERENCE,
    *,
    session: requests.Session | None = None,
) -> list[dict[str, str]]:
    payload = {
        "codigoTabelaReferencia": tabela_ref,
        "codigoTipoVeiculo": "1",
        "codigoMarca": codigo_marca,
    }
    data = post_fipe("ConsultarModelos", payload, session=session)
    return data.get("Modelos", []) if isinstance(data, dict) else []


def get_anos(
    codigo_marca: str,
    codigo_modelo: str,
    tabela_ref: str = DEFAULT_TABLE_REFERENCE,
    *,
    session: requests.Session | None = None,
) -> list[dict[str, str]]:
    payload = {
        "codigoTabelaReferencia": tabela_ref,
        "codigoTipoVeiculo": "1",
        "codigoMarca": codigo_marca,
        "codigoModelo": codigo_modelo,
    }
    return post_fipe("ConsultarAnoModelo", payload, session=session)


def consulta_fipe(
    codigo_marca: str,
    codigo_modelo: str,
    codigo_ano: str,
    tabela_ref: str = DEFAULT_TABLE_REFERENCE,
    *,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    ano, tipo_combustivel = codigo_ano.split("-", maxsplit=1)
    payload = {
        "codigoTabelaReferencia": tabela_ref,
        "codigoMarca": codigo_marca,
        "codigoModelo": codigo_modelo,
        "codigoTipoVeiculo": "1",
        "anoModelo": ano,
        "codigoTipoCombustivel": tipo_combustivel,
        "tipoVeiculo": "carro",
        "modeloCodigoExterno": "",
        "tipoConsulta": "tradicional",
    }
    return post_fipe("ConsultarValorComTodosParametros", payload, session=session)


def parse_price_response(response: dict[str, Any]) -> FipePrice:
    return FipePrice(
        marca=response.get("Marca"),
        modelo=response.get("Modelo"),
        ano_modelo=_safe_int(response.get("AnoModelo")),
        combustivel=response.get("Combustivel"),
        codigo_fipe=response.get("CodigoFipe"),
        mes_referencia=response.get("MesReferencia"),
        valor=parse_brl(response.get("Valor")),
        raw_valor=response.get("Valor"),
    )


def consultar_historico_modelo(
    codigo_marca: str,
    codigo_modelo: str,
    codigo_ano: str,
    tabela_ref: str = DEFAULT_TABLE_REFERENCE,
    *,
    months: int = 3,
    sleep_seconds: float = 0.0,
    session: requests.Session | None = None,
) -> list[FipePrice]:
    historico: list[FipePrice] = []
    current_ref = int(tabela_ref)

    for _ in range(months):
        response = consulta_fipe(
            codigo_marca,
            codigo_modelo,
            codigo_ano,
            str(current_ref),
            session=session,
        )
        if isinstance(response, dict) and "codigo" in response:
            break
        historico.append(parse_price_response(response))
        current_ref -= 1
        if sleep_seconds:
            time.sleep(sleep_seconds)

    return list(reversed(historico))


def parse_brl(value: str | None) -> int | None:
    if not value:
        return None
    digits = "".join(char for char in value if char.isdigit())
    return int(digits[:-2] or digits) if digits else None


def _safe_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
