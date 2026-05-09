from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Iterable

from .paths import DEFAULT_SQLITE_PATH


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE_PATH}")


def sqlite_path_from_url(database_url: str | None = None) -> Path:
    url = database_url or get_database_url()
    if not url.startswith("sqlite:///"):
        raise ValueError("Only sqlite:/// URLs are supported by the local loader.")
    return Path(url.removeprefix("sqlite:///"))


def connect_sqlite(database_url: str | None = None) -> sqlite3.Connection:
    path = sqlite_path_from_url(database_url)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def init_sqlite_db(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS mobiauto_listings (
            listing_id TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            fabricante TEXT,
            modelo TEXT,
            versao TEXT,
            modelo_fipe TEXT,
            valor INTEGER,
            valor_fipe INTEGER,
            cidade TEXT,
            ano TEXT,
            ano_fabricacao INTEGER,
            ano_modelo INTEGER,
            combustivel TEXT,
            km INTEGER,
            cambio TEXT,
            cor TEXT,
            carroceria TEXT,
            features TEXT,
            collected_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS fipe_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT,
            modelo TEXT,
            ano_modelo INTEGER,
            combustivel TEXT,
            codigo_fipe TEXT,
            mes_referencia TEXT,
            valor INTEGER,
            raw_valor TEXT,
            collected_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (codigo_fipe, mes_referencia)
        );
        """
    )
    _add_column_if_missing(connection, "mobiauto_listings", "valor_fipe", "INTEGER")
    connection.commit()


def upsert_listings(connection: sqlite3.Connection, listings: Iterable[dict[str, Any]]) -> int:
    rows = list(listings)
    for row in rows:
        payload = dict(row)
        if isinstance(payload.get("features"), list):
            payload["features"] = json.dumps(payload["features"], ensure_ascii=False)
        if not payload.get("listing_id"):
            payload["listing_id"] = payload["url"]

        connection.execute(
            """
            INSERT INTO mobiauto_listings (
                listing_id, url, fabricante, modelo, versao, modelo_fipe, valor,
                valor_fipe, cidade, ano, ano_fabricacao, ano_modelo, combustivel, km, cambio,
                cor, carroceria, features
            )
            VALUES (
                :listing_id, :url, :fabricante, :modelo, :versao, :modelo_fipe,
                :valor, :valor_fipe, :cidade, :ano, :ano_fabricacao, :ano_modelo, :combustivel,
                :km, :cambio, :cor, :carroceria, :features
            )
            ON CONFLICT(listing_id) DO UPDATE SET
                url=excluded.url,
                fabricante=excluded.fabricante,
                modelo=excluded.modelo,
                versao=excluded.versao,
                modelo_fipe=excluded.modelo_fipe,
                valor=excluded.valor,
                valor_fipe=excluded.valor_fipe,
                cidade=excluded.cidade,
                ano=excluded.ano,
                ano_fabricacao=excluded.ano_fabricacao,
                ano_modelo=excluded.ano_modelo,
                combustivel=excluded.combustivel,
                km=excluded.km,
                cambio=excluded.cambio,
                cor=excluded.cor,
                carroceria=excluded.carroceria,
                features=excluded.features,
                collected_at=CURRENT_TIMESTAMP
            """,
            payload,
        )

    connection.commit()
    return len(rows)


def _add_column_if_missing(
    connection: sqlite3.Connection,
    table_name: str,
    column_name: str,
    column_definition: str,
) -> None:
    columns = {
        row["name"]
        for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    }
    if column_name not in columns:
        connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")


def upsert_fipe_prices(connection: sqlite3.Connection, prices: Iterable[dict[str, Any]]) -> int:
    rows = list(prices)
    for row in rows:
        connection.execute(
            """
            INSERT INTO fipe_prices (
                marca, modelo, ano_modelo, combustivel, codigo_fipe,
                mes_referencia, valor, raw_valor
            )
            VALUES (
                :marca, :modelo, :ano_modelo, :combustivel, :codigo_fipe,
                :mes_referencia, :valor, :raw_valor
            )
            ON CONFLICT(codigo_fipe, mes_referencia) DO UPDATE SET
                marca=excluded.marca,
                modelo=excluded.modelo,
                ano_modelo=excluded.ano_modelo,
                combustivel=excluded.combustivel,
                valor=excluded.valor,
                raw_valor=excluded.raw_valor,
                collected_at=CURRENT_TIMESTAMP
            """,
            row,
        )

    connection.commit()
    return len(rows)
