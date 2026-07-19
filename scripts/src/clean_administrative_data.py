"""Pulizia di anagrafiche amministrative e procedimenti."""

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
    AUTHORITY_REQUIRED_COLUMNS,
    CLEAN_DATA_DIR,
    DATA_SOURCES,
    RAW_DATA_DIR,
    SOURCE_FILE_NAMES,
)
from scripts.utils import (  # noqa: E402
    configure_logging,
    create_output_directories,
    metadata_retrieved_at,
    normalize_authority_name,
    normalize_code,
    normalize_column_name,
    normalize_text,
    require_columns,
    save_dataframe,
    stable_identifier,
)

LOGGER = logging.getLogger(__name__)

PROCEDURE_COLUMNS = (
    "procedure_id",
    "procedure_name_original",
    "procedure_name_standardized",
    "procedure_type",
    "life_event",
    "economic_sector",
    "competent_authority",
    "authority_code",
    "territorial_level",
    "territorial_code",
    "legal_basis",
    "submission_channel",
    "statutory_deadline_days",
    "deadline_day_type",
    "silence_assent",
    "fee_eur",
    "digital_submission",
    "end_to_end_digital",
    "physical_presence_required",
    "source_id",
    "source_url",
    "retrieved_at",
)

IPA_COLUMN_RENAMES = {
    "codice_ipa": "authority_code",
    "denominazione_ente": "authority_name_original",
    "codice_fiscale_ente": "tax_code",
    "tipologia": "authority_type_original",
    "codice_categoria": "category_code",
    "codice_natura": "legal_nature_code",
    "codice_ateco": "ateco_code",
    "ente_in_liquidazione": "in_liquidation",
    "codice_miur": "miur_code",
    "codice_istat": "istat_authority_code",
    "acronimo": "acronym",
    "codice_comune_istat": "municipality_code",
    "codice_catastale_comune": "cadastral_code",
    "cap": "postal_code",
    "indirizzo": "address",
    "sito_istituzionale": "website",
    "data_aggiornamento": "source_updated_at",
}


def normalize_ipa_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Uniforma i nomi delle colonne IPA e applica la mappatura di progetto."""

    output = dataframe.copy()
    output.columns = [normalize_column_name(column) for column in output.columns]
    return output.rename(columns=IPA_COLUMN_RENAMES)


def infer_territorial_level(authority_type: Any, authority_name: Any) -> str:
    """Classifica il livello dell'ente usando tipologia e denominazione.

    Il criterio è operativo e non rappresenta una classificazione ufficiale
    delle competenze. Le categorie sono determinate con parole chiave ordinate
    dalla scala più specifica alla più generale.
    """

    text = " ".join(
        part for part in [normalize_text(authority_type), normalize_text(authority_name)] if part
    ).casefold()
    if not text:
        return "non_classificato"
    if "città metropolitana" in text or "citta metropolitana" in text:
        return "citta_metropolitana"
    if "comune" in text or "municipal" in text:
        return "comunale"
    if "provincia" in text:
        return "provinciale"
    if "regione" in text or "regionale" in text:
        return "regionale"
    if any(term in text for term in ("ministero", "agenzia nazionale", "presidenza del consiglio")):
        return "nazionale"
    return "altro"


def select_digital_address(row: pd.Series) -> str | None:
    """Seleziona una PEC IPA; usa la prima e-mail solo in assenza di PEC."""

    fallback: str | None = None
    for position in range(1, 6):
        mail = normalize_text(row.get(f"mail{position}"))
        mail_type = (normalize_text(row.get(f"tipo_mail{position}")) or "").casefold()
        if mail and fallback is None:
            fallback = mail
        if mail and "pec" in mail_type:
            return mail
    return fallback


def clean_ipa_entities(raw_path: Path | None = None) -> pd.DataFrame:
    """Pulisce il dataset IPA Enti e costruisce l'anagrafica standardizzata."""

    source = DATA_SOURCES["ipa_entities"]
    raw_path = raw_path or (RAW_DATA_DIR / SOURCE_FILE_NAMES["ipa_entities_raw"])
    metadata_path = RAW_DATA_DIR / SOURCE_FILE_NAMES["ipa_entities_metadata"]
    if not raw_path.exists():
        raise FileNotFoundError(
            f"File IPA non trovato: {raw_path}. Eseguire download_administrative_data.py."
        )

    raw_data = pd.read_excel(raw_path, dtype=str)
    if raw_data.empty:
        raise ValueError(f"Il file IPA è vuoto: {raw_path}")

    normalized = normalize_ipa_columns(raw_data)
    required_raw_columns = [
        "authority_code",
        "authority_name_original",
        "authority_type_original",
        "municipality_code",
        "website",
    ]
    require_columns(normalized, required_raw_columns, dataset_name="ipa_entities_raw")

    normalized["authority_code"] = normalized["authority_code"].map(normalize_code)
    normalized["authority_name_original"] = normalized["authority_name_original"].map(
        normalize_text
    )
    normalized["authority_name_standardized"] = normalized[
        "authority_name_original"
    ].map(normalize_authority_name)
    normalized["authority_type"] = normalized["authority_type_original"].map(normalize_text)
    normalized["municipality_code"] = normalized["municipality_code"].map(
        lambda value: normalize_code(value, width=6)
    )
    normalized["region_code"] = normalized["municipality_code"].str.slice(0, 2)
    normalized["province_code"] = normalized["municipality_code"].str.slice(0, 3)
    normalized["territorial_level"] = normalized.apply(
        lambda row: infer_territorial_level(
            row.get("authority_type_original"), row.get("authority_name_original")
        ),
        axis=1,
    )
    normalized["website"] = normalized["website"].map(normalize_text)
    normalized["digital_address"] = normalized.apply(select_digital_address, axis=1)
    normalized["authority_id"] = normalized.apply(
        lambda row: stable_identifier(
            "authority",
            row.get("authority_code"),
            row.get("authority_name_standardized"),
        ),
        axis=1,
    )
    normalized["source_id"] = source["source_id"]
    normalized["source_url"] = source["official_url"]
    normalized["retrieved_at"] = metadata_retrieved_at(metadata_path)

    preferred_columns = [
        "authority_id",
        "authority_code",
        "authority_name_original",
        "authority_name_standardized",
        "authority_type",
        "authority_type_original",
        "category_code",
        "legal_nature_code",
        "tax_code",
        "ateco_code",
        "in_liquidation",
        "istat_authority_code",
        "acronym",
        "territorial_level",
        "region_code",
        "province_code",
        "municipality_code",
        "cadastral_code",
        "postal_code",
        "address",
        "website",
        "digital_address",
        "source_updated_at",
        "source_id",
        "source_url",
        "retrieved_at",
    ]
    available_columns = [column for column in preferred_columns if column in normalized.columns]
    authorities = normalized[available_columns].copy()
    require_columns(authorities, AUTHORITY_REQUIRED_COLUMNS, dataset_name="authorities")
    return authorities


def build_empty_procedures() -> pd.DataFrame:
    """Crea la tabella procedimenti vuota finché non sono integrati cataloghi SUAP."""

    return pd.DataFrame(
        {column: pd.Series(dtype="string") for column in PROCEDURE_COLUMNS}
    )


def clean_administrative_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Pulisce le fonti amministrative e salva anagrafiche e procedimenti."""

    create_output_directories()
    authorities = clean_ipa_entities()
    procedures = build_empty_procedures()

    authorities_path = CLEAN_DATA_DIR / SOURCE_FILE_NAMES["authorities_clean"]
    authorities_csv_path = CLEAN_DATA_DIR / SOURCE_FILE_NAMES["authorities_clean_csv"]
    procedures_path = CLEAN_DATA_DIR / SOURCE_FILE_NAMES["procedures_clean"]

    sort_columns = ["territorial_level", "authority_type", "authority_name_standardized"]
    save_dataframe(authorities, authorities_path, sort_by=sort_columns)
    save_dataframe(authorities, authorities_csv_path, sort_by=sort_columns)
    save_dataframe(procedures, procedures_path, sort_by=["procedure_id"])
    LOGGER.info("Anagrafica IPA pulita: %s record", len(authorities))
    return authorities, procedures


def main() -> None:
    """Esegue la pulizia delle fonti amministrative."""

    configure_logging()
    clean_administrative_data()


if __name__ == "__main__":
    main()
