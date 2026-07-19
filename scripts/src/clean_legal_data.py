"""Pulizia e preparazione dei dati normativi."""

from __future__ import annotations

import logging
import re
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.config import (  # noqa: E402
    CLEAN_DATA_DIR,
    LEGAL_OBLIGATION_PATTERNS,
    SOURCE_FILE_NAMES,
)
from scripts.utils import configure_logging, create_output_directories, save_dataframe  # noqa: E402

LOGGER = logging.getLogger(__name__)

LEGAL_ACT_COLUMNS = (
    "act_id",
    "source_id",
    "act_type",
    "act_number",
    "act_year",
    "title",
    "issuing_authority",
    "publication_date",
    "effective_date",
    "repeal_date",
    "status",
    "territorial_scope",
    "official_identifier",
    "source_url",
    "retrieved_at",
    "content_hash",
)

LEGAL_PROVISION_COLUMNS = (
    "provision_id",
    "act_id",
    "article",
    "paragraph",
    "letter",
    "heading",
    "provision_text",
    "valid_from",
    "valid_to",
    "source_url",
    "retrieved_at",
)


def empty_string_dataframe(columns: tuple[str, ...]) -> pd.DataFrame:
    """Crea una tabella vuota con colonne stringa e schema esplicito."""

    return pd.DataFrame({column: pd.Series(dtype="string") for column in columns})


def flag_candidate_provisions(provisions: pd.DataFrame) -> pd.DataFrame:
    """Aggiunge flag trasparenti per selezionare disposizioni da validare.

    Le espressioni regolari individuano possibili obblighi, termini, rinnovi e
    sanzioni. I flag non classificano automaticamente una disposizione come
    onerosa e non vengono usati come misura diretta del carico burocratico.
    """

    output = provisions.copy()
    if "provision_text" not in output.columns:
        raise ValueError("La tabella delle disposizioni non contiene provision_text.")

    text = output["provision_text"].fillna("").astype(str)
    for flag_name, pattern in LEGAL_OBLIGATION_PATTERNS.items():
        output[f"candidate_{flag_name}"] = text.str.contains(
            re.compile(pattern, flags=re.IGNORECASE),
            regex=True,
            na=False,
        )
    candidate_columns = [column for column in output if column.startswith("candidate_")]
    output["candidate_for_review"] = output[candidate_columns].any(axis=1)
    return output


def clean_legal_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Prepara le tabelle normative disponibili e salva output con schema stabile.

    La prima versione non dispone ancora di un connettore Normattiva. Vengono
    quindi salvate tabelle vuote, prive di record simulati, che rendono stabile
    l'interfaccia per i passaggi successivi della pipeline.
    """

    create_output_directories()
    legal_acts = empty_string_dataframe(LEGAL_ACT_COLUMNS)
    legal_provisions = empty_string_dataframe(LEGAL_PROVISION_COLUMNS)
    legal_provisions = flag_candidate_provisions(legal_provisions)

    acts_path = CLEAN_DATA_DIR / SOURCE_FILE_NAMES["legal_acts_clean"]
    provisions_path = CLEAN_DATA_DIR / SOURCE_FILE_NAMES["legal_provisions_clean"]
    save_dataframe(legal_acts, acts_path, sort_by=["publication_date", "act_id"])
    save_dataframe(
        legal_provisions,
        provisions_path,
        sort_by=["act_id", "article", "paragraph", "letter"],
    )
    LOGGER.info(
        "Tabelle normative predisposte senza record simulati: %s, %s",
        acts_path,
        provisions_path,
    )
    return legal_acts, legal_provisions


def main() -> None:
    """Esegue la preparazione dei dati normativi."""

    configure_logging()
    clean_legal_data()


if __name__ == "__main__":
    main()
