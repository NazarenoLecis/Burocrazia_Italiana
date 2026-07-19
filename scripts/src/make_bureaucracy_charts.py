"""Generazione dei grafici descrittivi del progetto."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MaxNLocator

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.config import (  # noqa: E402
    CHART_DPI,
    CHART_TOP_CATEGORIES,
    CLEAN_DATA_DIR,
    DATA_SOURCES,
    INTERNATIONAL_CHARTS_DIR,
    PROCEDURE_CHARTS_DIR,
    PROCESSED_DATA_DIR,
    SOURCE_FILE_NAMES,
    TERRITORIAL_CHARTS_DIR,
)
from scripts.utils import (  # noqa: E402
    configure_logging,
    create_output_directories,
    read_dataframe,
)

LOGGER = logging.getLogger(__name__)


def save_figure(figure: plt.Figure, output_path: Path) -> Path:
    """Salva una figura PNG e chiude esplicitamente la risorsa grafica."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=CHART_DPI, bbox_inches="tight")
    plt.close(figure)
    LOGGER.info("Grafico salvato in %s", output_path)
    return output_path


def make_authority_type_chart(authorities: pd.DataFrame, output_path: Path) -> Path | None:
    """Rappresenta le tipologie di enti più frequenti nell'anagrafica IPA."""

    if authorities.empty or "authority_type" not in authorities.columns:
        LOGGER.info("Grafico tipologie enti omesso: dati non disponibili.")
        return None

    counts = (
        authorities["authority_type"]
        .fillna("Tipologia non disponibile")
        .value_counts()
        .head(CHART_TOP_CATEGORIES)
        .sort_values()
    )
    figure, axis = plt.subplots(figsize=(10, 7))
    counts.plot(kind="barh", ax=axis)
    axis.set_title("Enti presenti in IPA per tipologia")
    axis.set_xlabel("Numero di enti")
    axis.set_ylabel("")
    axis.grid(axis="x", alpha=0.25)
    figure.text(
        0.01,
        0.01,
        "Fonte: Indice delle Pubbliche Amministrazioni, dataset Enti. "
        "La numerosità non misura il carico burocratico.",
        fontsize=8,
    )
    figure.tight_layout(rect=(0, 0.05, 1, 1))
    return save_figure(figure, output_path)


def make_regional_digital_address_chart(
    comparisons: pd.DataFrame,
    output_path: Path,
) -> Path | None:
    """Rappresenta la quota di enti IPA con recapito digitale per regione sede."""

    indicator_name = "Quota di enti IPA con indirizzo digitale"
    data = comparisons.loc[comparisons["indicator_name"] == indicator_name].copy()
    if data.empty:
        LOGGER.info("Grafico territoriale omesso: indicatore non disponibile.")
        return None

    data["value_percent"] = pd.to_numeric(data["value"], errors="coerce") * 100
    data = data.dropna(subset=["value_percent"]).sort_values("value_percent")
    figure, axis = plt.subplots(figsize=(10, 7))
    axis.barh(data["territorial_name"], data["value_percent"])
    axis.set_title("Enti IPA con un indirizzo digitale valorizzato")
    axis.set_xlabel("Quota degli enti con sede nella regione (%)")
    axis.set_ylabel("")
    axis.set_xlim(0, 100)
    axis.grid(axis="x", alpha=0.25)
    figure.text(
        0.01,
        0.01,
        "Fonte: Indice delle Pubbliche Amministrazioni. Regione derivata dal comune sede. "
        "La presenza del recapito non misura la qualità del servizio.",
        fontsize=8,
    )
    figure.tight_layout(rect=(0, 0.06, 1, 1))
    return save_figure(figure, output_path)


def select_eurostat_series(indicators: pd.DataFrame) -> pd.DataFrame:
    """Seleziona una serie Eurostat comparabile per il grafico internazionale."""

    data = indicators.loc[
        indicators["source_id"] == DATA_SOURCES["eurostat_egovernment"]["source_id"]
    ].copy()
    if data.empty:
        return data

    if "indicator_code" in data.columns:
        preferred = data.loc[
            data["indicator_code"].astype(str).str.upper().eq("I_IGOVANYS")
        ]
        if not preferred.empty:
            data = preferred
        else:
            first_code = data["indicator_code"].dropna().astype(str).sort_values().iloc[0]
            data = data.loc[data["indicator_code"].astype(str) == first_code]

    if "breakdown_code" in data.columns:
        total_breakdown = data.loc[
            data["breakdown_code"].astype(str).str.upper().isin({"IND_TOTAL", "TOTAL"})
        ]
        if not total_breakdown.empty:
            data = total_breakdown

    if "unit_code" in data.columns:
        percentage_unit = data.loc[
            data["unit_code"].astype(str).str.upper().str.startswith("PC")
        ]
        if not percentage_unit.empty:
            data = percentage_unit
    return data


def make_eurostat_egovernment_chart(
    indicators: pd.DataFrame,
    output_path: Path,
) -> Path | None:
    """Rappresenta l'uso dei servizi pubblici online nei paesi selezionati."""

    data = select_eurostat_series(indicators)
    if data.empty:
        LOGGER.info("Grafico Eurostat omesso: dati non disponibili.")
        return None

    data["reference_period"] = pd.to_numeric(data["reference_period"], errors="coerce")
    data["value"] = pd.to_numeric(data["value"], errors="coerce")
    data = data.dropna(subset=["reference_period", "value"])
    if data.empty:
        return None

    pivot = data.pivot_table(
        index="reference_period",
        columns="territorial_name",
        values="value",
        aggfunc="first",
    ).sort_index()
    figure, axis = plt.subplots(figsize=(10, 6))
    pivot.plot(ax=axis, marker="o")
    indicator_label = str(data["indicator_name"].dropna().iloc[0])
    axis.set_title(indicator_label)
    axis.set_xlabel("Anno")
    axis.xaxis.set_major_locator(MaxNLocator(integer=True))
    axis.set_ylabel(str(data["unit"].dropna().iloc[0]))
    axis.grid(alpha=0.25)
    axis.legend(title="Territorio", frameon=False)
    figure.text(
        0.01,
        0.01,
        "Fonte: Eurostat, dataset isoc_ciegi_ac. Indicatore di utilizzo dei servizi "
        "pubblici online; non misura direttamente tempi o costi burocratici.",
        fontsize=8,
    )
    figure.tight_layout(rect=(0, 0.06, 1, 1))
    return save_figure(figure, output_path)


def make_bureaucracy_charts() -> list[Path]:
    """Genera tutti i grafici consentiti dai dati disponibili."""

    create_output_directories()
    authorities = read_dataframe(CLEAN_DATA_DIR / SOURCE_FILE_NAMES["authorities_clean"])
    comparisons = read_dataframe(
        PROCESSED_DATA_DIR / SOURCE_FILE_NAMES["territorial_comparisons"]
    )
    indicators = read_dataframe(
        PROCESSED_DATA_DIR / SOURCE_FILE_NAMES["bureaucracy_indicators"]
    )

    chart_paths = [
        make_authority_type_chart(
            authorities,
            PROCEDURE_CHARTS_DIR / "ipa_authorities_by_type.png",
        ),
        make_regional_digital_address_chart(
            comparisons,
            TERRITORIAL_CHARTS_DIR / "ipa_digital_address_by_region.png",
        ),
        make_eurostat_egovernment_chart(
            indicators,
            INTERNATIONAL_CHARTS_DIR / "eurostat_egovernment_comparison.png",
        ),
    ]
    return [path for path in chart_paths if path is not None]


def main() -> None:
    """Esegue la generazione dei grafici."""

    configure_logging()
    make_bureaucracy_charts()


if __name__ == "__main__":
    main()
