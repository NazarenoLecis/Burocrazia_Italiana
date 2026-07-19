"""Costruzione dell'inventario documentato delle fonti del progetto."""

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
    DATA_SOURCES,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    SOURCE_FILE_NAMES,
    SOURCE_INVENTORY_REQUIRED_COLUMNS,
    SOURCE_STATUS_VALUES,
)
from scripts.utils import (  # noqa: E402
    configure_logging,
    create_output_directories,
    metadata_retrieved_at,
    require_columns,
    save_dataframe,
)

LOGGER = logging.getLogger(__name__)

METADATA_FILE_BY_SOURCE = {
    "ipa_entities": SOURCE_FILE_NAMES["ipa_entities_metadata"],
    "eurostat_egovernment": SOURCE_FILE_NAMES["eurostat_egovernment_metadata"],
}


def build_source_record(source: dict[str, Any]) -> dict[str, Any]:
    """Trasforma una configurazione di fonte in un record dell'inventario."""

    source_id = source["source_id"]
    metadata_file_name = METADATA_FILE_BY_SOURCE.get(source_id)
    last_successful_update = None
    if metadata_file_name:
        last_successful_update = metadata_retrieved_at(RAW_DATA_DIR / metadata_file_name)

    return {
        "source_id": source_id,
        "source_name": source["source_name"],
        "institution": source["institution"],
        "source_category": source["source_category"],
        "geographical_coverage": source["geographical_coverage"],
        "time_coverage_start": source["time_coverage_start"],
        "time_coverage_end": source["time_coverage_end"],
        "update_frequency": source["update_frequency"],
        "access_method": source["access_method"],
        "file_format": source["file_format"],
        "official_url": source["official_url"],
        "automated_download": source["automated_download"],
        "authentication_required": source["authentication_required"],
        "license": source["license"],
        "last_successful_update": last_successful_update,
        "status": source["status"],
        "coverage_notes": source["coverage_notes"],
        "limitations": source["limitations"],
    }


def validate_source_statuses(source_inventory: pd.DataFrame) -> None:
    """Verifica che lo stato di ogni fonte appartenga alla classificazione ammessa."""

    invalid_statuses = sorted(
        set(source_inventory["status"].dropna()) - set(SOURCE_STATUS_VALUES)
    )
    if invalid_statuses:
        raise ValueError(f"Stati fonte non ammessi: {', '.join(invalid_statuses)}")


def build_source_inventory() -> pd.DataFrame:
    """Costruisce e salva l'inventario delle fonti censite.

    Returns
    -------
    pandas.DataFrame
        Una riga per fonte con copertura, accesso, stato e limitazioni.
    """

    create_output_directories()
    records = [build_source_record(source) for source in DATA_SOURCES.values()]
    source_inventory = pd.DataFrame(records)
    require_columns(
        source_inventory,
        SOURCE_INVENTORY_REQUIRED_COLUMNS,
        dataset_name="source_inventory",
    )
    validate_source_statuses(source_inventory)

    output_path = PROCESSED_DATA_DIR / SOURCE_FILE_NAMES["source_inventory"]
    save_dataframe(source_inventory, output_path, sort_by=["source_category", "source_id"])
    LOGGER.info("Inventario delle fonti salvato in %s", output_path)
    return source_inventory


def main() -> None:
    """Esegue la costruzione dell'inventario delle fonti."""

    configure_logging()
    build_source_inventory()


if __name__ == "__main__":
    main()
