from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

import pandas as pd
from rapidfuzz import fuzz, process


@dataclass(frozen=True)
class MatchResult:
    value: str | None
    score: float


def normalize_vehicle_name(value: str | None) -> str:
    if not value:
        return ""

    text = unicodedata.normalize("NFKD", value)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\b(flex|gasolina|alcool|diesel|eletricidade|hibrido)\b", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def find_best_match(
    query: str,
    choices: list[str],
    *,
    min_score: float = 70,
) -> MatchResult:
    if not query or not choices:
        return MatchResult(value=None, score=0)

    normalized_choices = {normalize_vehicle_name(choice): choice for choice in choices if choice}
    match = process.extractOne(
        normalize_vehicle_name(query),
        list(normalized_choices.keys()),
        scorer=fuzz.WRatio,
    )
    if not match:
        return MatchResult(value=None, score=0)

    normalized_value, score, _ = match
    value = normalized_choices[normalized_value]
    return MatchResult(value=value if score >= min_score else None, score=float(score))


def find_similar_fipe_model(
    model_name: str,
    model_oem: str,
    candidates: pd.DataFrame,
    *,
    model_year: int | None = None,
    brand_column: str = "Marca",
    model_column: str = "Modelo",
    year_column: str | None = None,
    min_score: float = 70,
) -> MatchResult:
    df = candidates.copy()
    if brand_column in df.columns:
        df = df[df[brand_column].astype(str).str.casefold() == str(model_oem).casefold()]

    if model_year is not None and year_column and year_column in df.columns:
        df = df[df[year_column] == model_year]

    choices = df[model_column].dropna().astype(str).unique().tolist()
    return find_best_match(model_name, choices, min_score=min_score)
