"""Costruzione di indicatori elementari sulla burocrazia e sul contesto."""

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
    INDICATOR_REQUIRED_COLUMNS,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    SOURCE_FILE_NAMES,
)
from scripts.utils import (  # noqa: E402
    configure_logging,
    create_output_directories,
    jsonstat_to_dataframe,
    normalize_column_name,
    normalize_text,
    read_dataframe,
    read_json,
    require_columns,
    safe_share,
    save_dataframe,
    stable_identifier,
)

LOGGER = logging.getLogger(__name__)


def empty_indicator_dataframe() -> pd.DataFrame:
    """Crea una tabella indicatori vuota con lo schema minimo del progetto."""

    return pd.DataFrame(
        {column: pd.Series(dtype="object") for column in INDICATOR_REQUIRED_COLUMNS}
    )


def reference_date_from_authorities(authorities: pd.DataFrame) -> str:
    """Determina il periodo di riferimento usando metadati IPA disponibili."""

    for column in ("retrieved_at", "source_updated_at"):
        if column in authorities.columns:
            values = authorities[column].dropna().astype(str)
            if not values.empty:
                return values.max()[:10]
    return ""


def build_authority_registry_indicators(authorities: pd.DataFrame) -> pd.DataFrame:
    """Costruisce indicatori descrittivi sull'anagrafica IPA.

    Gli indicatori misurano numerosità e disponibilità di recapiti digitali nel
    registro IPA. Non rappresentano qualità dei servizi, tempi amministrativi o
    carico burocratico sostenuto dagli utenti.
    """

    if authorities.empty:
        return empty_indicator_dataframe()

    reference_period = reference_date_from_authorities(authorities)
    source = DATA_SOURCES["ipa_entities"]
    groups: list[tuple[str, pd.DataFrame]] = [("Totale", authorities)]
    if "authority_type" in authorities.columns:
        for authority_type, group in authorities.groupby("authority_type", dropna=False):
            label = normalize_text(authority_type) or "Tipologia non disponibile"
            groups.append((label, group))

    records: list[dict[str, Any]] = []
    for group_label, group in groups:
        total = len(group)
        measures = (
            (
                "authority_count",
                f"Numero di enti IPA - {group_label}",
                float(total),
                "enti",
                "Conteggio dei record presenti nel dataset IPA Enti.",
            ),
            (
                "website_available_share",
                f"Quota di enti con sito istituzionale - {group_label}",
                safe_share(group["website"].notna().sum(), total),
                "quota",
                "Quota di record IPA con campo Sito_istituzionale valorizzato.",
            ),
            (
                "digital_address_available_share",
                f"Quota di enti con indirizzo digitale - {group_label}",
                safe_share(group["digital_address"].notna().sum(), total),
                "quota",
                "Quota di record IPA con almeno un recapito e-mail o PEC valorizzato.",
            ),
        )
        for measure_code, indicator_name, value, unit, methodology in measures:
            records.append(
                {
                    "indicator_id": stable_identifier(
                        "indicator", source["source_id"], measure_code, group_label, reference_period
                    ),
                    "indicator_name": indicator_name,
                    "dimension": "administrative_registry_coverage",
                    "territorial_level": "nazionale",
                    "territorial_code": "IT",
                    "territorial_name": "Italia",
                    "reference_period": reference_period,
                    "value": value,
                    "unit": unit,
                    "observation_count": total,
                    "source_id": source["source_id"],
                    "source_url": source["official_url"],
                    "methodology": methodology,
                    "indicator_code": measure_code,
                    "breakdown_name": "authority_type",
                    "breakdown_value": group_label,
                }
            )
    return pd.DataFrame(records)


def prepare_eurostat_long_data(raw_path: Path | None = None) -> pd.DataFrame:
    """Converte il JSON-stat Eurostat in una tabella lunga e la salva."""

    raw_path = raw_path or (RAW_DATA_DIR / SOURCE_FILE_NAMES["eurostat_egovernment_raw"])
    if not raw_path.exists():
        LOGGER.info("Dati Eurostat non disponibili; indicatori internazionali omessi.")
        return pd.DataFrame()

    payload = read_json(raw_path)
    long_data = jsonstat_to_dataframe(payload)
    long_data.columns = [normalize_column_name(column) for column in long_data.columns]
    long_data["value"] = pd.to_numeric(long_data["value"], errors="coerce")
    long_data = long_data.loc[long_data["value"].notna()].copy()
    output_path = CLEAN_DATA_DIR / SOURCE_FILE_NAMES["eurostat_egovernment_clean"]
    save_dataframe(
        long_data,
        output_path,
        sort_by=["indic_is", "ind_type", "unit", "geo", "time"],
    )
    return long_data


def build_eurostat_context_indicators(long_data: pd.DataFrame) -> pd.DataFrame:
    """Standardizza le osservazioni Eurostat come indicatori di contesto.

    I valori misurano l'uso dei servizi pubblici online. Sono mantenuti separati
    dagli indicatori diretti su documenti, costi, passaggi e tempi procedurali.
    """

    if long_data.empty:
        return empty_indicator_dataframe()

    source = DATA_SOURCES["eurostat_egovernment"]
    records: list[dict[str, Any]] = []
    for row in long_data.to_dict(orient="records"):
        indicator_code = normalize_text(row.get("indic_is")) or "unknown_indicator"
        indicator_label = normalize_text(row.get("indic_is_label")) or indicator_code
        breakdown_code = normalize_text(row.get("ind_type")) or ""
        breakdown_label = normalize_text(row.get("ind_type_label")) or breakdown_code
        unit_code = normalize_text(row.get("unit")) or ""
        unit_label = normalize_text(row.get("unit_label")) or unit_code
        geo_code = normalize_text(row.get("geo")) or ""
        geo_label = normalize_text(row.get("geo_label")) or geo_code
        reference_period = normalize_text(row.get("time")) or ""
        territorial_level = (
            "european_aggregate" if geo_code.startswith(("EU", "EA")) else "country"
        )

        records.append(
            {
                "indicator_id": stable_identifier(
                    "indicator",
                    source["source_id"],
                    indicator_code,
                    breakdown_code,
                    unit_code,
                    geo_code,
                    reference_period,
                ),
                "indicator_name": indicator_label,
                "dimension": "digital_public_services_context",
                "territorial_level": territorial_level,
                "territorial_code": geo_code,
                "territorial_name": geo_label,
                "reference_period": reference_period,
                "value": row.get("value"),
                "unit": unit_label,
                "observation_count": 1,
                "source_id": source["source_id"],
                "source_url": source["official_url"],
                "methodology": (
                    "Osservazione ufficiale Eurostat dal dataset isoc_ciegi_ac. "
                    "È un indicatore di utilizzo dei servizi pubblici online."
                ),
                "indicator_code": indicator_code,
                "breakdown_name": "ind_type",
                "breakdown_value": breakdown_label,
                "breakdown_code": breakdown_code,
                "unit_code": unit_code,
                "status": row.get("status"),
            }
        )
    return pd.DataFrame(records)


def build_bureaucracy_indicators() -> pd.DataFrame:
    """Costruisce e salva gli indicatori elementari disponibili."""

    create_output_directories()
    authorities_path = CLEAN_DATA_DIR / SOURCE_FILE_NAMES["authorities_clean"]
    authorities = read_dataframe(authorities_path)

    authority_indicators = build_authority_registry_indicators(authorities)
    eurostat_long = prepare_eurostat_long_data()
    eurostat_indicators = build_eurostat_context_indicators(eurostat_long)

    indicators = pd.concat(
        [authority_indicators, eurostat_indicators],
        ignore_index=True,
        sort=False,
    )
    if indicators.empty:
        indicators = empty_indicator_dataframe()
    require_columns(indicators, INDICATOR_REQUIRED_COLUMNS, dataset_name="bureaucracy_indicators")

    parquet_path = PROCESSED_DATA_DIR / SOURCE_FILE_NAMES["bureaucracy_indicators"]
    csv_path = PROCESSED_DATA_DIR / SOURCE_FILE_NAMES["bureaucracy_indicators_csv"]
    sort_columns = [
        "dimension",
        "indicator_code",
        "territorial_code",
        "reference_period",
        "breakdown_code",
    ]
    save_dataframe(indicators, parquet_path, sort_by=sort_columns)
    save_dataframe(indicators, csv_path, sort_by=sort_columns)
    LOGGER.info("Indicatori salvati: %s record", len(indicators))
    return indicators


def main() -> None:
    """Esegue la costruzione degli indicatori disponibili."""

    configure_logging()
    build_bureaucracy_indicators()


if __name__ == "__main__":
    main()
