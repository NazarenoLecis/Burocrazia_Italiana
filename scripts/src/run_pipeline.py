"""Esecuzione sequenziale della pipeline del progetto."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.src.build_bureaucracy_indicators import (  # noqa: E402
    build_bureaucracy_indicators,
)
from scripts.src.build_source_inventory import build_source_inventory  # noqa: E402
from scripts.src.build_territorial_comparisons import (  # noqa: E402
    build_territorial_comparisons,
)
from scripts.src.check_data_quality import check_data_quality  # noqa: E402
from scripts.src.clean_administrative_data import clean_administrative_data  # noqa: E402
from scripts.src.clean_legal_data import clean_legal_data  # noqa: E402
from scripts.src.download_administrative_data import (  # noqa: E402
    download_administrative_data,
)
from scripts.src.download_legal_data import download_legal_data  # noqa: E402
from scripts.src.download_statistical_data import download_statistical_data  # noqa: E402
from scripts.src.make_bureaucracy_charts import make_bureaucracy_charts  # noqa: E402
from scripts.utils import configure_logging, create_output_directories  # noqa: E402

LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Esegue download, pulizia, indicatori, controlli e grafici in sequenza."""

    configure_logging()
    create_output_directories()

    LOGGER.info("1/11 - Costruzione inventario iniziale delle fonti")
    build_source_inventory()

    LOGGER.info("2/11 - Acquisizione dati normativi")
    download_legal_data()

    LOGGER.info("3/11 - Acquisizione dati amministrativi")
    download_administrative_data()

    LOGGER.info("4/11 - Acquisizione dati statistici")
    download_statistical_data(continue_on_optional_error=True)

    LOGGER.info("5/11 - Pulizia dati normativi")
    clean_legal_data()

    LOGGER.info("6/11 - Pulizia dati amministrativi")
    clean_administrative_data()

    LOGGER.info("7/11 - Costruzione indicatori")
    build_bureaucracy_indicators()

    LOGGER.info("8/11 - Costruzione confronti territoriali")
    build_territorial_comparisons()

    LOGGER.info("9/11 - Aggiornamento inventario con gli esiti dei download")
    build_source_inventory()

    LOGGER.info("10/11 - Controlli di qualità")
    check_data_quality()

    LOGGER.info("11/11 - Generazione grafici")
    chart_paths = make_bureaucracy_charts()
    LOGGER.info("Pipeline completata. Grafici prodotti: %s", len(chart_paths))


if __name__ == "__main__":
    main()
