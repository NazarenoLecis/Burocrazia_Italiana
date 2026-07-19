"""Funzioni generali riutilizzabili per acquisizione, pulizia e validazione."""

from __future__ import annotations

import hashlib
import json
import logging
import math
import re
import time
import unicodedata
from datetime import date, datetime, timezone
from itertools import product
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd
import requests

from scripts.config import (
    HTTP_MAX_ATTEMPTS,
    HTTP_RETRY_BACKOFF_SECONDS,
    HTTP_TIMEOUT_SECONDS,
    MAX_FILE_AGE_DAYS,
    OUTPUT_DIRECTORIES,
    USER_AGENT,
)

LOGGER = logging.getLogger(__name__)


def configure_logging(level: int = logging.INFO) -> None:
    """Configura un formato di logging uniforme per gli script del progetto."""

    if logging.getLogger().handlers:
        return
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def create_output_directories(directories: Iterable[Path] = OUTPUT_DIRECTORIES) -> None:
    """Crea le cartelle di output mancanti.

    Parameters
    ----------
    directories:
        Percorsi da creare. Per impostazione predefinita usa le cartelle
        definite in ``scripts/config.py``.
    """

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def normalize_column_name(value: str) -> str:
    """Converte un nome di colonna in formato snake_case ASCII."""

    normalized = unicodedata.normalize("NFKD", str(value))
    ascii_value = "".join(char for char in normalized if not unicodedata.combining(char))
    ascii_value = re.sub(r"[^A-Za-z0-9]+", "_", ascii_value)
    return ascii_value.strip("_").lower()


def normalize_text(value: Any) -> str | None:
    """Normalizza spazi e forma Unicode di una stringa.

    Parameters
    ----------
    value:
        Valore originale. Può essere nullo o non testuale.

    Returns
    -------
    str | None
        Testo normalizzato, oppure ``None`` quando l'input è mancante.
    """

    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    text = unicodedata.normalize("NFKC", str(value)).strip()
    text = re.sub(r"\s+", " ", text)
    return text or None


def normalize_authority_name(value: Any) -> str | None:
    """Normalizza il nome di un'amministrazione per confronti deterministici.

    Il criterio conserva le parole significative, uniforma maiuscole,
    punteggiatura e spazi. Non elimina forme giuridiche perché possono essere
    informative per distinguere enti con denominazioni simili.
    """

    text = normalize_text(value)
    if text is None:
        return None
    text = text.upper()
    text = re.sub(r"[\.,;:_/\\\-]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_code(value: Any, width: int | None = None) -> str | None:
    """Normalizza un codice eliminando il suffisso decimale e applicando zeri.

    Parameters
    ----------
    value:
        Codice originario.
    width:
        Lunghezza minima desiderata. Gli zeri sono aggiunti a sinistra.

    Returns
    -------
    str | None
        Codice normalizzato oppure ``None`` per input mancanti.
    """

    text = normalize_text(value)
    if text is None:
        return None
    text = re.sub(r"\.0$", "", text)
    text = re.sub(r"\s+", "", text)
    return text.zfill(width) if width else text


def normalize_italian_number(value: Any) -> float | None:
    """Converte numeri italiani con punto delle migliaia e virgola decimale."""

    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, (int, float, np.number)):
        return float(value)

    text = normalize_text(value)
    if text is None:
        return None
    text = text.replace("€", "").replace("%", "").replace(" ", "")
    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    try:
        return float(text)
    except ValueError as error:
        raise ValueError(f"Valore numerico non interpretabile: {value!r}") from error


def parse_date_value(value: Any) -> pd.Timestamp | pd.NaT:
    """Converte un valore in data pandas senza sostituire errori con valori."""

    text = normalize_text(value)
    if text is None:
        return pd.NaT
    return pd.to_datetime(text, errors="coerce", dayfirst=True)


def stable_identifier(namespace: str, *values: Any, length: int = 20) -> str:
    """Crea un identificatore deterministico a partire da valori stabili."""

    normalized_values = [normalize_text(value) or "" for value in values]
    payload = "|".join([namespace, *normalized_values]).encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()[:length]
    return f"{namespace}_{digest}"


def calculate_file_hash(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Calcola l'hash SHA-256 di un file."""

    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        while chunk := file_handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def file_is_fresh(path: Path, max_age_days: int = MAX_FILE_AGE_DAYS) -> bool:
    """Verifica se un file esiste ed è più recente della soglia indicata."""

    if not path.exists() or path.stat().st_size == 0:
        return False
    age_seconds = time.time() - path.stat().st_mtime
    return age_seconds <= max_age_days * 24 * 60 * 60


def request_with_retries(
    url: str,
    *,
    params: Mapping[str, Any] | Sequence[tuple[str, Any]] | None = None,
    timeout: int = HTTP_TIMEOUT_SECONDS,
    max_attempts: int = HTTP_MAX_ATTEMPTS,
) -> requests.Response:
    """Esegue una richiesta HTTP GET con timeout e tentativi limitati.

    Solleva l'ultima eccezione di rete o HTTP se tutti i tentativi falliscono.
    Le risposte 4xx non sono ripetute, salvo 408 e 429. Le risposte 5xx sono
    ripetute perché possono dipendere da indisponibilità temporanee.
    """

    session = requests.Session()
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    last_error: requests.RequestException | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            response = session.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout,
                allow_redirects=True,
            )
            if response.status_code >= 400:
                response.raise_for_status()
            return response
        except requests.HTTPError as error:
            last_error = error
            status_code = error.response.status_code if error.response is not None else None
            retryable = status_code in {408, 429} or (status_code is not None and status_code >= 500)
            if not retryable or attempt == max_attempts:
                raise
        except (requests.ConnectionError, requests.Timeout) as error:
            last_error = error
            if attempt == max_attempts:
                raise

        sleep_seconds = HTTP_RETRY_BACKOFF_SECONDS * attempt
        LOGGER.warning(
            "Tentativo %s/%s fallito per %s. Nuovo tentativo tra %s secondi.",
            attempt,
            max_attempts,
            url,
            sleep_seconds,
        )
        time.sleep(sleep_seconds)

    if last_error is not None:
        raise last_error
    raise RuntimeError(f"Richiesta non completata senza eccezione esplicita: {url}")


def download_file(
    url: str,
    destination: Path,
    *,
    force: bool = False,
    max_age_days: int = MAX_FILE_AGE_DAYS,
    params: Mapping[str, Any] | Sequence[tuple[str, Any]] | None = None,
) -> dict[str, Any]:
    """Scarica un file con scrittura atomica e restituisce i metadati.

    Il download viene evitato quando il file è recente e ``force`` è falso.
    Il contenuto grezzo non viene trasformato durante questa operazione.
    """

    destination.parent.mkdir(parents=True, exist_ok=True)
    checked_at = datetime.now(timezone.utc).isoformat()

    if not force and file_is_fresh(destination, max_age_days=max_age_days):
        retrieved_at = datetime.fromtimestamp(
            destination.stat().st_mtime, tz=timezone.utc
        ).isoformat()
        return {
            "path": str(destination),
            "request_url": url,
            "resolved_url": url,
            "retrieved_at": retrieved_at,
            "checked_at": checked_at,
            "downloaded": False,
            "sha256": calculate_file_hash(destination),
            "content_type": None,
            "content_length": destination.stat().st_size,
            "http_status": None,
        }

    response = request_with_retries(url, params=params)
    retrieved_at = checked_at
    temporary_path = destination.with_suffix(destination.suffix + ".part")
    temporary_path.write_bytes(response.content)
    if temporary_path.stat().st_size == 0:
        temporary_path.unlink(missing_ok=True)
        raise ValueError(f"La fonte ha restituito un file vuoto: {response.url}")
    temporary_path.replace(destination)

    return {
        "path": str(destination),
        "request_url": url,
        "resolved_url": response.url,
        "retrieved_at": retrieved_at,
        "checked_at": checked_at,
        "downloaded": True,
        "sha256": calculate_file_hash(destination),
        "content_type": response.headers.get("Content-Type"),
        "content_length": destination.stat().st_size,
        "http_status": response.status_code,
        "etag": response.headers.get("ETag"),
        "last_modified": response.headers.get("Last-Modified"),
    }


def write_json(data: Mapping[str, Any] | Sequence[Any], path: Path) -> None:
    """Salva dati JSON in UTF-8 con formattazione leggibile."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )


def read_json(path: Path) -> Any:
    """Legge un file JSON e restituisce il contenuto Python."""

    if not path.exists():
        raise FileNotFoundError(f"File JSON non trovato: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def download_json(
    url: str,
    destination: Path,
    *,
    params: Mapping[str, Any] | Sequence[tuple[str, Any]] | None = None,
    force: bool = False,
    max_age_days: int = MAX_FILE_AGE_DAYS,
) -> dict[str, Any]:
    """Scarica una risposta JSON preservando il testo ricevuto dalla fonte."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    checked_at = datetime.now(timezone.utc).isoformat()

    if not force and file_is_fresh(destination, max_age_days=max_age_days):
        read_json(destination)
        retrieved_at = datetime.fromtimestamp(
            destination.stat().st_mtime, tz=timezone.utc
        ).isoformat()
        return {
            "path": str(destination),
            "request_url": url,
            "resolved_url": url,
            "retrieved_at": retrieved_at,
            "checked_at": checked_at,
            "downloaded": False,
            "sha256": calculate_file_hash(destination),
            "content_type": "application/json",
            "content_length": destination.stat().st_size,
            "http_status": None,
        }

    response = request_with_retries(url, params=params)
    retrieved_at = checked_at
    try:
        response.json()
    except requests.JSONDecodeError as error:
        raise ValueError(f"Risposta JSON non valida dalla fonte: {response.url}") from error

    temporary_path = destination.with_suffix(destination.suffix + ".part")
    temporary_path.write_bytes(response.content)
    temporary_path.replace(destination)

    return {
        "path": str(destination),
        "request_url": url,
        "resolved_url": response.url,
        "retrieved_at": retrieved_at,
        "checked_at": checked_at,
        "downloaded": True,
        "sha256": calculate_file_hash(destination),
        "content_type": response.headers.get("Content-Type"),
        "content_length": destination.stat().st_size,
        "http_status": response.status_code,
        "etag": response.headers.get("ETag"),
        "last_modified": response.headers.get("Last-Modified"),
    }


def read_dataframe(path: Path, **kwargs: Any) -> pd.DataFrame:
    """Legge un dataset tabellare in base all'estensione del file."""

    if not path.exists():
        raise FileNotFoundError(f"Dataset non trovato: {path}")
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path, **kwargs)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path, **kwargs)
    if suffix == ".parquet":
        return pd.read_parquet(path, **kwargs)
    if suffix == ".json":
        return pd.read_json(path, **kwargs)
    raise ValueError(f"Formato tabellare non supportato: {path.suffix}")


def save_dataframe(
    dataframe: pd.DataFrame,
    path: Path,
    *,
    index: bool = False,
    sort_by: Sequence[str] | None = None,
) -> None:
    """Salva un dataframe con ordinamento esplicito e formato determinato.

    Parameters
    ----------
    dataframe:
        Tabella da salvare.
    path:
        Percorso finale in ``output``.
    index:
        Indica se salvare l'indice pandas.
    sort_by:
        Colonne usate per ordinare i record. Sono considerate solo le colonne
        effettivamente presenti.
    """

    output = dataframe.copy()
    if sort_by:
        valid_sort_columns = [column for column in sort_by if column in output.columns]
        if valid_sort_columns:
            output = output.sort_values(valid_sort_columns, kind="stable", na_position="last")
    path.parent.mkdir(parents=True, exist_ok=True)

    suffix = path.suffix.lower()
    if suffix == ".csv":
        output.to_csv(path, index=index)
    elif suffix == ".parquet":
        output.to_parquet(path, index=index)
    elif suffix in {".xlsx", ".xls"}:
        output.to_excel(path, index=index)
    elif suffix == ".json":
        output.to_json(path, orient="records", force_ascii=False, indent=2)
    else:
        raise ValueError(f"Formato di salvataggio non supportato: {path.suffix}")


def validate_required_columns(
    dataframe: pd.DataFrame,
    required_columns: Sequence[str],
) -> list[str]:
    """Restituisce l'elenco delle colonne obbligatorie assenti."""

    return [column for column in required_columns if column not in dataframe.columns]


def require_columns(
    dataframe: pd.DataFrame,
    required_columns: Sequence[str],
    *,
    dataset_name: str,
) -> None:
    """Solleva un errore leggibile quando mancano colonne obbligatorie."""

    missing_columns = validate_required_columns(dataframe, required_columns)
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise ValueError(f"Colonne mancanti in {dataset_name}: {missing_text}")


def duplicate_mask(dataframe: pd.DataFrame, columns: Sequence[str]) -> pd.Series:
    """Identifica duplicati sulle colonne disponibili senza eliminare record."""

    available_columns = [column for column in columns if column in dataframe.columns]
    if not available_columns:
        return pd.Series(False, index=dataframe.index, dtype=bool)
    return dataframe.duplicated(subset=available_columns, keep=False)


def safe_share(numerator: int | float, denominator: int | float) -> float | None:
    """Calcola una quota e restituisce ``None`` quando il denominatore è zero."""

    if denominator == 0 or pd.isna(denominator):
        return None
    return float(numerator) / float(denominator)


def metadata_retrieved_at(metadata_path: Path) -> str | None:
    """Legge la data di acquisizione da un manifest di download."""

    if not metadata_path.exists():
        return None
    metadata = read_json(metadata_path)
    value = metadata.get("retrieved_at") if isinstance(metadata, dict) else None
    return normalize_text(value)


def jsonstat_to_dataframe(payload: Mapping[str, Any]) -> pd.DataFrame:
    """Converte un dataset JSON-stat 2.0 in formato tabellare lungo.

    Il criterio segue l'ordine delle dimensioni dichiarato in ``id`` e assume
    l'ordinamento row-major previsto da JSON-stat, in cui l'ultima dimensione
    varia più rapidamente. Sono conservati codici, etichette e valori nulli.
    """

    dimension_ids = list(payload.get("id", []))
    dimension_sizes = list(payload.get("size", []))
    dimensions = payload.get("dimension", {})
    values = payload.get("value", [])
    statuses = payload.get("status", {})

    if not dimension_ids or len(dimension_ids) != len(dimension_sizes):
        raise ValueError("Struttura JSON-stat priva di dimensioni valide.")

    ordered_codes: list[list[str]] = []
    labels_by_dimension: dict[str, Mapping[str, str]] = {}

    for dimension_id, expected_size in zip(dimension_ids, dimension_sizes, strict=True):
        dimension = dimensions.get(dimension_id, {})
        category = dimension.get("category", {})
        index = category.get("index", {})
        labels_by_dimension[dimension_id] = category.get("label", {})

        if isinstance(index, dict):
            codes = [code for code, _ in sorted(index.items(), key=lambda item: item[1])]
        elif isinstance(index, list):
            codes = [str(code) for code in index]
        else:
            raise ValueError(f"Indice JSON-stat non supportato per {dimension_id}.")

        if len(codes) != expected_size:
            raise ValueError(
                f"Dimensione {dimension_id}: attesi {expected_size} codici, trovati {len(codes)}."
            )
        ordered_codes.append(codes)

    total_cells = math.prod(dimension_sizes)

    def value_at(position: int) -> Any:
        """Restituisce il valore associato a una posizione piatta."""

        if isinstance(values, dict):
            return values.get(str(position), values.get(position))
        if isinstance(values, list) and position < len(values):
            return values[position]
        return None

    def status_at(position: int) -> Any:
        """Restituisce il flag di stato associato a una posizione piatta."""

        if isinstance(statuses, dict):
            return statuses.get(str(position), statuses.get(position))
        if isinstance(statuses, list) and position < len(statuses):
            return statuses[position]
        return None

    rows: list[dict[str, Any]] = []
    for flat_position, coordinate in enumerate(product(*ordered_codes)):
        if flat_position >= total_cells:
            break
        row: dict[str, Any] = {}
        for dimension_id, code in zip(dimension_ids, coordinate, strict=True):
            row[dimension_id] = code
            row[f"{dimension_id}_label"] = labels_by_dimension[dimension_id].get(code, code)
        row["value"] = value_at(flat_position)
        row["status"] = status_at(flat_position)
        rows.append(row)

    dataframe = pd.DataFrame(rows)
    dataframe.attrs["dataset_label"] = payload.get("label")
    dataframe.attrs["source"] = payload.get("source")
    dataframe.attrs["updated"] = payload.get("updated")
    return dataframe


def current_utc_date() -> str:
    """Restituisce la data corrente UTC in formato ISO."""

    return date.today().isoformat()
