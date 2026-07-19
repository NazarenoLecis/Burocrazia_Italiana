"""Controlli automatici sulla struttura e sulla qualità dei dataset."""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.config import (  # noqa: E402
    AUTHORITY_REQUIRED_COLUMNS,
    CLEAN_DATA_DIR,
    INDICATOR_REQUIRED_COLUMNS,
    PROCESSED_DATA_DIR,
    QUALITY_DATA_DIR,
    QUALITY_WARNING_MISSING_SHARE,
    SOURCE_FILE_NAMES,
    SOURCE_INVENTORY_REQUIRED_COLUMNS,
    SOURCE_STATUS_VALUES,
    TERRITORIAL_COMPARISON_REQUIRED_COLUMNS,
)
from scripts.utils import (  # noqa: E402
    configure_logging,
    create_output_directories,
    duplicate_mask,
    read_dataframe,
    safe_share,
    save_dataframe,
    validate_required_columns,
)

LOGGER = logging.getLogger(__name__)


def quality_record(
    check_name: str,
    dataset_name: str,
    check_status: str,
    affected_rows: int,
    total_rows: int,
    severity: str,
    description: str,
) -> dict[str, Any]:
    """Costruisce un record standardizzato per il report di qualità."""

    return {
        "check_name": check_name,
        "dataset_name": dataset_name,
        "check_status": check_status,
        "affected_rows": int(affected_rows),
        "total_rows": int(total_rows),
        "affected_share": safe_share(affected_rows, total_rows),
        "severity": severity,
        "description": description,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def check_required_columns(
    dataframe: pd.DataFrame,
    dataset_name: str,
    required_columns: Sequence[str],
) -> dict[str, Any]:
    """Controlla la presenza delle colonne obbligatorie."""

    missing_columns = validate_required_columns(dataframe, required_columns)
    status = "pass" if not missing_columns else "fail"
    description = (
        "Tutte le colonne obbligatorie sono presenti."
        if not missing_columns
        else f"Colonne mancanti: {', '.join(missing_columns)}"
    )
    return quality_record(
        "required_columns",
        dataset_name,
        status,
        len(missing_columns),
        len(required_columns),
        "error" if missing_columns else "info",
        description,
    )


def check_duplicate_keys(
    dataframe: pd.DataFrame,
    dataset_name: str,
    key_columns: Sequence[str],
) -> dict[str, Any]:
    """Controlla chiavi duplicate senza rimuovere automaticamente record."""

    duplicates = duplicate_mask(dataframe, key_columns)
    affected_rows = int(duplicates.sum())
    return quality_record(
        "duplicate_keys",
        dataset_name,
        "pass" if affected_rows == 0 else "fail",
        affected_rows,
        len(dataframe),
        "error" if affected_rows else "info",
        f"Chiave controllata: {', '.join(key_columns)}.",
    )


def check_missing_values(
    dataframe: pd.DataFrame,
    dataset_name: str,
    column: str,
    *,
    severity: str = "warning",
) -> dict[str, Any]:
    """Misura i valori mancanti in una colonna senza sostituirli con zero."""

    if column not in dataframe.columns:
        return quality_record(
            f"missing_{column}",
            dataset_name,
            "fail",
            1,
            1,
            "error",
            f"Colonna assente: {column}.",
        )
    affected_rows = int(dataframe[column].isna().sum())
    missing_share = safe_share(affected_rows, len(dataframe)) or 0.0
    status = "warn" if missing_share > QUALITY_WARNING_MISSING_SHARE else "pass"
    return quality_record(
        f"missing_{column}",
        dataset_name,
        status,
        affected_rows,
        len(dataframe),
        severity if status == "warn" else "info",
        (
            f"Quota mancante confrontata con la soglia "
            f"{QUALITY_WARNING_MISSING_SHARE:.0%}."
        ),
    )


def check_numeric_range(
    dataframe: pd.DataFrame,
    dataset_name: str,
    column: str,
    *,
    minimum: float | None = None,
    maximum: float | None = None,
) -> dict[str, Any]:
    """Segnala valori numerici esterni all'intervallo metodologicamente ammesso."""

    if column not in dataframe.columns:
        return quality_record(
            f"range_{column}",
            dataset_name,
            "fail",
            1,
            1,
            "error",
            f"Colonna assente: {column}.",
        )
    values = pd.to_numeric(dataframe[column], errors="coerce")
    invalid = pd.Series(False, index=dataframe.index)
    if minimum is not None:
        invalid = invalid | (values < minimum)
    if maximum is not None:
        invalid = invalid | (values > maximum)
    affected_rows = int(invalid.fillna(False).sum())
    bounds = f"min={minimum}, max={maximum}"
    return quality_record(
        f"range_{column}",
        dataset_name,
        "pass" if affected_rows == 0 else "fail",
        affected_rows,
        len(dataframe),
        "error" if affected_rows else "info",
        f"Intervallo controllato: {bounds}.",
    )


def load_dataset_or_record_failure(
    path: Path,
    dataset_name: str,
    records: list[dict[str, Any]],
) -> pd.DataFrame | None:
    """Carica un dataset o aggiunge al report un errore di file mancante."""

    if not path.exists():
        records.append(
            quality_record(
                "file_exists",
                dataset_name,
                "fail",
                1,
                1,
                "error",
                f"File non trovato: {path}",
            )
        )
        return None
    dataframe = read_dataframe(path)
    records.append(
        quality_record(
            "file_exists",
            dataset_name,
            "pass",
            0,
            len(dataframe),
            "info",
            f"File disponibile: {path}",
        )
    )
    return dataframe


def add_standard_checks(
    records: list[dict[str, Any]],
    dataframe: pd.DataFrame,
    dataset_name: str,
    required_columns: Sequence[str],
    key_columns: Sequence[str] | None = None,
) -> None:
    """Aggiunge controlli strutturali condivisi per un dataset."""

    records.append(check_required_columns(dataframe, dataset_name, required_columns))
    if key_columns:
        records.append(check_duplicate_keys(dataframe, dataset_name, key_columns))


def check_data_quality() -> pd.DataFrame:
    """Esegue i controlli disponibili e salva un report senza modificare i dati."""

    create_output_directories()
    records: list[dict[str, Any]] = []

    datasets: list[
        tuple[str, Path, Sequence[str], Sequence[str] | None, Callable[[pd.DataFrame], None] | None]
    ] = [
        (
            "source_inventory",
            PROCESSED_DATA_DIR / SOURCE_FILE_NAMES["source_inventory"],
            SOURCE_INVENTORY_REQUIRED_COLUMNS,
            ["source_id"],
            None,
        ),
        (
            "authorities",
            CLEAN_DATA_DIR / SOURCE_FILE_NAMES["authorities_clean"],
            AUTHORITY_REQUIRED_COLUMNS,
            ["authority_id"],
            None,
        ),
        (
            "bureaucracy_indicators",
            PROCESSED_DATA_DIR / SOURCE_FILE_NAMES["bureaucracy_indicators"],
            INDICATOR_REQUIRED_COLUMNS,
            ["indicator_id"],
            None,
        ),
        (
            "territorial_comparisons",
            PROCESSED_DATA_DIR / SOURCE_FILE_NAMES["territorial_comparisons"],
            TERRITORIAL_COMPARISON_REQUIRED_COLUMNS,
            ["indicator_name", "territorial_code", "reference_period"],
            None,
        ),
    ]

    loaded: dict[str, pd.DataFrame] = {}
    for dataset_name, path, required_columns, key_columns, _ in datasets:
        dataframe = load_dataset_or_record_failure(path, dataset_name, records)
        if dataframe is None:
            continue
        loaded[dataset_name] = dataframe
        add_standard_checks(records, dataframe, dataset_name, required_columns, key_columns)

    source_inventory = loaded.get("source_inventory")
    if source_inventory is not None and "status" in source_inventory.columns:
        invalid_status = ~source_inventory["status"].isin(SOURCE_STATUS_VALUES)
        affected_rows = int(invalid_status.sum())
        records.append(
            quality_record(
                "valid_source_status",
                "source_inventory",
                "pass" if affected_rows == 0 else "fail",
                affected_rows,
                len(source_inventory),
                "error" if affected_rows else "info",
                "Gli stati devono appartenere alla classificazione definita in config.py.",
            )
        )

    authorities = loaded.get("authorities")
    if authorities is not None:
        records.append(check_missing_values(authorities, "authorities", "source_url"))
        records.append(check_missing_values(authorities, "authorities", "municipality_code"))
        records.append(check_missing_values(authorities, "authorities", "website"))

    indicators = loaded.get("bureaucracy_indicators")
    if indicators is not None:
        records.append(check_missing_values(indicators, "bureaucracy_indicators", "value"))
        records.append(
            check_numeric_range(
                indicators,
                "bureaucracy_indicators",
                "observation_count",
                minimum=0,
            )
        )

    comparisons = loaded.get("territorial_comparisons")
    if comparisons is not None:
        records.append(
            check_numeric_range(
                comparisons,
                "territorial_comparisons",
                "coverage_rate",
                minimum=0,
                maximum=1,
            )
        )
        records.append(
            check_numeric_range(
                comparisons,
                "territorial_comparisons",
                "observation_count",
                minimum=0,
            )
        )

    quality_report = pd.DataFrame(records)
    output_path = QUALITY_DATA_DIR / SOURCE_FILE_NAMES["data_quality_report"]
    save_dataframe(
        quality_report,
        output_path,
        sort_by=["severity", "dataset_name", "check_name"],
    )
    LOGGER.info("Report di qualità salvato in %s", output_path)
    return quality_report


def main() -> None:
    """Esegue i controlli di qualità."""

    configure_logging()
    check_data_quality()


if __name__ == "__main__":
    main()
