"""Acquisizione di dati statistici per contesto e confronti internazionali."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.config import (  # noqa: E402
    DATA_SOURCES,
    EUROSTAT_EGOVERNMENT_QUERY,
    FORCE_DOWNLOAD,
    RAW_DATA_DIR,
    SOURCE_FILE_NAMES,
)
from scripts.utils import (  # noqa: E402
    configure_logging,
    create_output_directories,
    download_json,
    write_json,
)

LOGGER = logging.getLogger(__name__)


def build_eurostat_egovernment_url() -> str:
    """Costruisce l'URL documentato per il dataset Eurostat selezionato."""

    source = DATA_SOURCES["eurostat_egovernment"]
    return f"{source['api_base_url']}/{source['dataset_code']}"


def download_eurostat_egovernment(force_download: bool = FORCE_DOWNLOAD) -> Path:
    """Scarica il dataset JSON-stat Eurostat sui servizi pubblici online."""

    source = DATA_SOURCES["eurostat_egovernment"]
    target_path = RAW_DATA_DIR / SOURCE_FILE_NAMES["eurostat_egovernment_raw"]
    metadata_path = RAW_DATA_DIR / SOURCE_FILE_NAMES["eurostat_egovernment_metadata"]
    url = build_eurostat_egovernment_url()

    download_metadata = download_json(
        url,
        target_path,
        params=EUROSTAT_EGOVERNMENT_QUERY,
        force=force_download,
    )
    query_string = urlencode(EUROSTAT_EGOVERNMENT_QUERY, doseq=True)
    metadata: dict[str, Any] = {
        "source_id": source["source_id"],
        "source_name": source["source_name"],
        "institution": source["institution"],
        "official_url": source["official_url"],
        "dataset_code": source["dataset_code"],
        "query_url": f"{url}?{query_string}",
        "license": source["license"],
        "extraction_method": "api",
        **download_metadata,
    }
    write_json(metadata, metadata_path)
    LOGGER.info("Dataset Eurostat disponibile in %s", target_path)
    return target_path


def download_statistical_data(
    force_download: bool = FORCE_DOWNLOAD,
    *,
    continue_on_optional_error: bool = True,
) -> list[Path]:
    """Scarica le fonti statistiche implementate.

    Parameters
    ----------
    force_download:
        Forza l'aggiornamento dei file esistenti.
    continue_on_optional_error:
        Se vero, registra l'errore di una fonte opzionale e prosegue.

    Returns
    -------
    list[pathlib.Path]
        File scaricati o già disponibili localmente.
    """

    create_output_directories()
    paths: list[Path] = []
    try:
        paths.append(download_eurostat_egovernment(force_download=force_download))
    except (requests.RequestException, ValueError, OSError) as error:
        if not continue_on_optional_error:
            raise
        LOGGER.warning(
            "Fonte opzionale eurostat_egovernment non acquisita: %s",
            error,
        )
    return paths


def main() -> None:
    """Esegue il download delle fonti statistiche implementate."""

    configure_logging()
    download_statistical_data()


if __name__ == "__main__":
    main()
