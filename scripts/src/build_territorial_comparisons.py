"""Costruzione di confronti territoriali con controlli di copertura."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.config import (  # noqa: E402
    CLEAN_DATA_DIR,
    DATA_SOURCES,
    ITALIAN_REGION_NAMES,
    PROCESSED_DATA_DIR,
    QUALITY_MIN_OBSERVATIONS,
    SOURCE_FILE_NAMES,
    TERRITORIAL_COMPARISON_REQUIRED_COLUMNS,
)
from scripts.utils import (  # noqa: E402
    configure_logging,
    create_output_directories,
    read_dataframe,
    require_columns,
    safe_share,
    save_dataframe,
)

LOGGER = logging.getLogger(__name__)


def infer_reference_period(authorities: pd.DataFrame) -> str:
    """Ricava il periodo di riferimento più recente disponibile nell'anagrafica."""

    for column in ("retrieved_at", "source_updated_at"):
        if column in authorities.columns:
            values = authorities[column].dropna().astype(str)
            if not values.empty:
                return values.max()[:10]
    return ""


def assign_quality_flag(observation_count: int, coverage_rate: float | None) -> str:
    """Assegna un flag usando numerosità minima e copertura territoriale."""

    if observation_count < QUALITY_MIN_OBSERVATIONS:
        return "insufficient_observations"
    if coverage_rate is None or coverage_rate < 0.80:
        return "limited_coverage"
    return "sufficient"


def build_regional_authority_comparisons(authorities: pd.DataFrame) -> pd.DataFrame:
    """Confronta la disponibilità di recapiti IPA per regione della sede.

    La regione deriva dal codice ISTAT del comune in cui ha sede l'ente. Il
    risultato descrive la localizzazione dell'anagrafica e non l'estensione
    territoriale delle competenze dell'ente.
    """

    if authorities.empty:
        return pd.DataFrame(columns=TERRITORIAL_COMPARISON_REQUIRED_COLUMNS)

    valid_region_codes = set(ITALIAN_REGION_NAMES)
    valid_region_mask = authorities["region_code"].isin(valid_region_codes)
    valid_authorities = authorities.loc[valid_region_mask].copy()
    coverage_rate = safe_share(valid_region_mask.sum(), len(authorities))
    reference_period = infer_reference_period(authorities)
    source = DATA_SOURCES["ipa_entities"]

    records: list[dict[str, Any]] = []
    for region_code, group in valid_authorities.groupby("region_code", dropna=False):
        observation_count = len(group)
        quality_flag = assign_quality_flag(observation_count, coverage_rate)
        measures = (
            ("Numero di enti IPA con sede nella regione", float(observation_count), "enti"),
            (
                "Quota di enti IPA con sito istituzionale",
                safe_share(group["website"].notna().sum(), observation_count),
                "quota",
            ),
            (
                "Quota di enti IPA con indirizzo digitale",
                safe_share(group["digital_address"].notna().sum(), observation_count),
                "quota",
            ),
        )
        for indicator_name, value, unit in measures:
            records.append(
                {
                    "indicator_name": indicator_name,
                    "territorial_level": "regionale",
                    "territorial_code": region_code,
                    "territorial_name": ITALIAN_REGION_NAMES.get(region_code, region_code),
                    "reference_period": reference_period,
                    "value": value,
                    "unit": unit,
                    "observation_count": observation_count,
                    "coverage_rate": coverage_rate,
                    "source_count": 1,
                    "quality_flag": quality_flag,
                    "source_id": source["source_id"],
                    "source_url": source["official_url"],
                    "methodology_note": (
                        "Regione derivata dalle prime due cifre del codice ISTAT del comune sede."
                    ),
                }
            )
    if not records:
        return pd.DataFrame(
            {
                column: pd.Series(dtype="object")
                for column in TERRITORIAL_COMPARISON_REQUIRED_COLUMNS
            }
        )
    return pd.DataFrame(records)


def build_territorial_comparisons() -> pd.DataFrame:
    """Costruisce e salva i confronti territoriali disponibili."""

    create_output_directories()
    authorities_path = CLEAN_DATA_DIR / SOURCE_FILE_NAMES["authorities_clean"]
    authorities = read_dataframe(authorities_path)
    comparisons = build_regional_authority_comparisons(authorities)
    require_columns(
        comparisons,
        TERRITORIAL_COMPARISON_REQUIRED_COLUMNS,
        dataset_name="territorial_comparisons",
    )

    parquet_path = PROCESSED_DATA_DIR / SOURCE_FILE_NAMES["territorial_comparisons"]
    csv_path = PROCESSED_DATA_DIR / SOURCE_FILE_NAMES["territorial_comparisons_csv"]
    sort_columns = ["indicator_name", "territorial_code", "reference_period"]
    save_dataframe(comparisons, parquet_path, sort_by=sort_columns)
    save_dataframe(comparisons, csv_path, sort_by=sort_columns)
    LOGGER.info("Confronti territoriali salvati: %s record", len(comparisons))
    return comparisons


def main() -> None:
    """Esegue la costruzione dei confronti territoriali."""

    configure_logging()
    build_territorial_comparisons()


if __name__ == "__main__":
    main()
