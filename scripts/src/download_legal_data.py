"""Acquisizione delle fonti normative ufficiali."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.config import DATA_SOURCES  # noqa: E402
from scripts.utils import configure_logging, create_output_directories  # noqa: E402

LOGGER = logging.getLogger(__name__)


def list_pending_legal_connectors() -> list[str]:
    """Restituisce le fonti normative censite prive di connettore automatico."""

    return [
        source_id
        for source_id, source in DATA_SOURCES.items()
        if source["source_category"] == "legislation"
        and not source["automated_download"]
    ]


def download_legal_data() -> list[Path]:
    """Esegue i connettori normativi disponibili.

    La prima versione non invoca endpoint Normattiva non ancora configurati.
    La funzione restituisce una lista vuota e registra in modo esplicito le
    fonti censite ancora da implementare, senza creare dati simulati.
    """

    create_output_directories()
    pending_connectors = list_pending_legal_connectors()
    if pending_connectors:
        LOGGER.info(
            "Connettori normativi non ancora implementati: %s",
            ", ".join(pending_connectors),
        )
    return []


def main() -> None:
    """Esegue l'acquisizione delle fonti normative implementate."""

    configure_logging()
    download_legal_data()


if __name__ == "__main__":
    main()
