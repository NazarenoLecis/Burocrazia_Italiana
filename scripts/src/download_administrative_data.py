"""Acquisizione di anagrafiche e dati sui procedimenti amministrativi."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.config import (  # noqa: E402
    DATA_SOURCES,
    FORCE_DOWNLOAD,
    RAW_DATA_DIR,
    SOURCE_FILE_NAMES,
)
from scripts.utils import (  # noqa: E402
    configure_logging,
    create_output_directories,
    download_file,
    write_json,
)

LOGGER = logging.getLogger(__name__)


def download_ipa_entities(force_download: bool = FORCE_DOWNLOAD) -> Path:
    """Scarica il dataset ufficiale IPA sugli enti.

    Parameters
    ----------
    force_download:
        Se vero, ignora la validità temporale del file locale.

    Returns
    -------
    pathlib.Path
        Percorso del file XLSX grezzo.
    """

    source = DATA_SOURCES["ipa_entities"]
    target_path = RAW_DATA_DIR / SOURCE_FILE_NAMES["ipa_entities_raw"]
    metadata_path = RAW_DATA_DIR / SOURCE_FILE_NAMES["ipa_entities_metadata"]

    download_metadata = download_file(
        source["download_url"],
        target_path,
        force=force_download,
    )
    metadata: dict[str, Any] = {
        "source_id": source["source_id"],
        "source_name": source["source_name"],
        "institution": source["institution"],
        "official_url": source["official_url"],
        "license": source["license"],
        "extraction_method": "structured_download",
        **download_metadata,
    }
    write_json(metadata, metadata_path)
    LOGGER.info("Dataset IPA disponibile in %s", target_path)
    return target_path


def download_administrative_data(force_download: bool = FORCE_DOWNLOAD) -> list[Path]:
    """Scarica le fonti amministrative implementate.

    Le fonti dichiarate obbligatorie propagano gli errori di rete o formato,
    così la pipeline non produce output apparentemente completi su dati assenti.
    """

    create_output_directories()
    downloaded_paths = [download_ipa_entities(force_download=force_download)]
    return downloaded_paths


def main() -> None:
    """Esegue il download delle fonti amministrative implementate."""

    configure_logging()
    download_administrative_data()


if __name__ == "__main__":
    main()
