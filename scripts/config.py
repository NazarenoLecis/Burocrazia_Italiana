"""Configurazioni centrali del progetto Burocrazia italiana."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = PROJECT_ROOT / "output"
DATA_DIR = OUTPUT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
CLEAN_DATA_DIR = DATA_DIR / "clean"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
QUALITY_DATA_DIR = DATA_DIR / "quality"

CHARTS_DIR = OUTPUT_DIR / "charts"
LEGAL_CHARTS_DIR = CHARTS_DIR / "legal_complexity"
PROCEDURE_CHARTS_DIR = CHARTS_DIR / "administrative_procedures"
TERRITORIAL_CHARTS_DIR = CHARTS_DIR / "territorial_comparisons"
INTERNATIONAL_CHARTS_DIR = CHARTS_DIR / "international_comparisons"

OUTPUT_DIRECTORIES = (
    RAW_DATA_DIR,
    CLEAN_DATA_DIR,
    PROCESSED_DATA_DIR,
    QUALITY_DATA_DIR,
    LEGAL_CHARTS_DIR,
    PROCEDURE_CHARTS_DIR,
    TERRITORIAL_CHARTS_DIR,
    INTERNATIONAL_CHARTS_DIR,
)

ANALYSIS_START_YEAR = 2022
ANALYSIS_END_YEAR = 2026
FORCE_DOWNLOAD = False
MAX_FILE_AGE_DAYS = 7
HTTP_TIMEOUT_SECONDS = 60
HTTP_MAX_ATTEMPTS = 3
HTTP_RETRY_BACKOFF_SECONDS = 2
USER_AGENT = (
    "Burocrazia_Italiana/0.1 "
    "(+https://github.com/NazarenoLecis/Burocrazia_Italiana)"
)

SOURCE_STATUS_VALUES = (
    "active",
    "partially_available",
    "manual_only",
    "temporarily_unavailable",
    "not_implemented",
    "excluded",
)

SOURCE_FILE_NAMES = {
    "ipa_entities_raw": "ipa_entities.xlsx",
    "ipa_entities_metadata": "ipa_entities.metadata.json",
    "eurostat_egovernment_raw": "eurostat_isoc_ciegi_ac.json",
    "eurostat_egovernment_metadata": "eurostat_isoc_ciegi_ac.metadata.json",
    "source_inventory": "source_inventory.csv",
    "legal_acts_clean": "legal_acts.parquet",
    "legal_provisions_clean": "legal_provisions.parquet",
    "authorities_clean": "authorities.parquet",
    "authorities_clean_csv": "authorities.csv",
    "procedures_clean": "administrative_procedures.parquet",
    "eurostat_egovernment_clean": "eurostat_egovernment_long.parquet",
    "bureaucracy_indicators": "bureaucracy_indicators.parquet",
    "bureaucracy_indicators_csv": "bureaucracy_indicators.csv",
    "territorial_comparisons": "territorial_comparisons.parquet",
    "territorial_comparisons_csv": "territorial_comparisons.csv",
    "data_quality_report": "data_quality_report.csv",
}

DATA_SOURCES = {
    "ipa_entities": {
        "source_id": "ipa_entities",
        "source_name": "Indice delle Pubbliche Amministrazioni - Enti",
        "institution": "Agenzia per l'Italia Digitale",
        "source_category": "administrative_registry",
        "geographical_coverage": "Italia",
        "time_coverage_start": "",
        "time_coverage_end": "",
        "update_frequency": "giornaliera",
        "access_method": "structured_download",
        "file_format": "XLSX",
        "official_url": "https://indicepa.gov.it/ipa-dati/dataset/enti",
        "download_url": (
            "https://indicepa.gov.it/ipa-dati/dataset/"
            "5baa3eb8-266e-455a-8de8-b1f434c279b2/resource/"
            "d09adf99-dc10-4349-8c53-27b1e5aa97b6/download/enti.xlsx"
        ),
        "automated_download": True,
        "authentication_required": False,
        "license": "CC BY 4.0",
        "required": True,
        "status": "active",
        "coverage_notes": "Anagrafica degli enti presenti in IPA.",
        "limitations": (
            "La sede dell'ente non coincide necessariamente con il territorio "
            "sul quale l'ente esercita le proprie competenze."
        ),
    },
    "normattiva_open_data": {
        "source_id": "normattiva_open_data",
        "source_name": "Normattiva Open Data",
        "institution": "Presidenza del Consiglio dei ministri e IPZS",
        "source_category": "legislation",
        "geographical_coverage": "Italia",
        "time_coverage_start": "",
        "time_coverage_end": "",
        "update_frequency": "continuo",
        "access_method": "api",
        "file_format": "XML, JSON e altri formati aperti",
        "official_url": "https://dati.normattiva.it/",
        "documentation_url": "https://dati.normattiva.it/Come-scaricare-i-dati",
        "automated_download": False,
        "authentication_required": False,
        "license": "Condizioni indicate dal portale",
        "required": False,
        "status": "not_implemented",
        "coverage_notes": "Atti normativi in versione originaria, vigente e multivigente.",
        "limitations": "Il connettore API deve essere configurato sulla specifica OpenAPI ufficiale.",
    },
    "gazzetta_ufficiale": {
        "source_id": "gazzetta_ufficiale",
        "source_name": "Gazzetta Ufficiale della Repubblica Italiana",
        "institution": "Istituto Poligrafico e Zecca dello Stato",
        "source_category": "legislation",
        "geographical_coverage": "Italia",
        "time_coverage_start": "",
        "time_coverage_end": "",
        "update_frequency": "giornaliera",
        "access_method": "web",
        "file_format": "HTML e PDF",
        "official_url": "https://www.gazzettaufficiale.it/",
        "automated_download": False,
        "authentication_required": False,
        "license": "Da verificare per ogni modalità di riuso",
        "required": False,
        "status": "not_implemented",
        "coverage_notes": "Pubblicazione ufficiale degli atti della Repubblica italiana.",
        "limitations": "Preferire Normattiva per testi strutturati e multivigenza.",
    },
    "eur_lex": {
        "source_id": "eur_lex",
        "source_name": "EUR-Lex",
        "institution": "Ufficio delle pubblicazioni dell'Unione europea",
        "source_category": "legislation",
        "geographical_coverage": "Unione europea",
        "time_coverage_start": "",
        "time_coverage_end": "",
        "update_frequency": "continuo",
        "access_method": "api",
        "file_format": "XML, RDF e altri formati",
        "official_url": "https://eur-lex.europa.eu/",
        "automated_download": False,
        "authentication_required": False,
        "license": "Decisione 2011/833/UE e condizioni del portale",
        "required": False,
        "status": "not_implemented",
        "coverage_notes": "Diritto e documenti ufficiali dell'Unione europea.",
        "limitations": "Il perimetro deve essere definito tramite CELEX, ELI e relazioni tra atti.",
    },
    "dati_gov_it": {
        "source_id": "dati_gov_it",
        "source_name": "Catalogo nazionale dei dati aperti",
        "institution": "Dipartimento per la trasformazione digitale",
        "source_category": "data_catalogue",
        "geographical_coverage": "Italia",
        "time_coverage_start": "",
        "time_coverage_end": "",
        "update_frequency": "variabile",
        "access_method": "catalogue_api",
        "file_format": "DCAT-AP_IT e metadati catalografici",
        "official_url": "https://www.dati.gov.it/",
        "automated_download": False,
        "authentication_required": False,
        "license": "Variabile per dataset",
        "required": False,
        "status": "not_implemented",
        "coverage_notes": "Catalogo di scoperta; i dati vanno acquisiti dalle fonti originarie.",
        "limitations": "Qualità, copertura e aggiornamento variano tra enti titolari.",
    },
    "catalogo_ssu": {
        "source_id": "catalogo_ssu",
        "source_name": "Catalogo del Sistema degli Sportelli Unici",
        "institution": "Sistema Impresa in un Giorno",
        "source_category": "administrative_procedures",
        "geographical_coverage": "Italia",
        "time_coverage_start": "",
        "time_coverage_end": "",
        "update_frequency": "variabile",
        "access_method": "e_service",
        "file_format": "Dati strutturati tramite servizi interoperabili",
        "official_url": "https://catalogo.impresainungiorno.gov.it/",
        "automated_download": False,
        "authentication_required": True,
        "license": "Da verificare",
        "required": False,
        "status": "manual_only",
        "coverage_notes": "Procedimenti e componenti del sistema SUAP.",
        "limitations": "L'accesso operativo può richiedere accreditamento e fruizione tramite PDND.",
    },
    "anac_open_data": {
        "source_id": "anac_open_data",
        "source_name": "ANAC Open Data",
        "institution": "Autorità Nazionale Anticorruzione",
        "source_category": "public_procurement",
        "geographical_coverage": "Italia",
        "time_coverage_start": "",
        "time_coverage_end": "",
        "update_frequency": "variabile",
        "access_method": "api_and_download",
        "file_format": "JSON, CSV e OCDS",
        "official_url": "https://dati.anticorruzione.it/",
        "automated_download": False,
        "authentication_required": False,
        "license": "Indicata per ciascun dataset",
        "required": False,
        "status": "not_implemented",
        "coverage_notes": "Contratti pubblici e informazioni collegate alla BDNCP.",
        "limitations": "Gli indicatori procedurali richiedono definizioni coerenti delle fasi temporali.",
    },
    "istat": {
        "source_id": "istat",
        "source_name": "IstatData e servizi SDMX",
        "institution": "Istituto nazionale di statistica",
        "source_category": "official_statistics",
        "geographical_coverage": "Italia",
        "time_coverage_start": "",
        "time_coverage_end": "",
        "update_frequency": "variabile",
        "access_method": "sdmx_api",
        "file_format": "SDMX",
        "official_url": "https://esploradati.istat.it/",
        "automated_download": False,
        "authentication_required": False,
        "license": "Licenza Istat",
        "required": False,
        "status": "not_implemented",
        "coverage_notes": "Statistiche su imprese, territori, PA e digitalizzazione.",
        "limitations": "Le misure di percezione vanno distinte da tempi e costi osservati.",
    },
    "eurostat_egovernment": {
        "source_id": "eurostat_egovernment",
        "source_name": "Eurostat - E-government activities of individuals",
        "institution": "Eurostat",
        "source_category": "official_statistics",
        "geographical_coverage": "Italia, UE e paesi selezionati",
        "time_coverage_start": str(ANALYSIS_START_YEAR),
        "time_coverage_end": str(ANALYSIS_END_YEAR),
        "update_frequency": "annuale",
        "access_method": "api",
        "file_format": "JSON-stat 2.0",
        "official_url": "https://ec.europa.eu/eurostat/data/database",
        "api_base_url": (
            "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
        ),
        "dataset_code": "isoc_ciegi_ac",
        "automated_download": True,
        "authentication_required": False,
        "license": "Eurostat reuse policy",
        "required": False,
        "status": "active",
        "coverage_notes": "Uso dei servizi pubblici online da parte degli individui.",
        "limitations": "Indicatore di utilizzo e contesto digitale; non misura direttamente l'onere burocratico.",
    },
    "oecd_pmr": {
        "source_id": "oecd_pmr",
        "source_name": "OECD Product Market Regulation",
        "institution": "OECD",
        "source_category": "international_indicators",
        "geographical_coverage": "Paesi OECD e altre economie",
        "time_coverage_start": "",
        "time_coverage_end": "",
        "update_frequency": "periodica",
        "access_method": "sdmx_api",
        "file_format": "SDMX",
        "official_url": "https://www.oecd.org/en/topics/product-market-regulation.html",
        "automated_download": False,
        "authentication_required": False,
        "license": "OECD terms and conditions",
        "required": False,
        "status": "not_implemented",
        "coverage_notes": "Indicatori su barriere regolatorie e oneri amministrativi.",
        "limitations": "Indicatori compositi e comparabili a livello nazionale, non procedimenti puntuali.",
    },
    "world_bank_bready": {
        "source_id": "world_bank_bready",
        "source_name": "World Bank Business Ready",
        "institution": "World Bank",
        "source_category": "international_indicators",
        "geographical_coverage": "Economie incluse nel programma B-READY",
        "time_coverage_start": "2024",
        "time_coverage_end": "2025",
        "update_frequency": "annuale",
        "access_method": "structured_download",
        "file_format": "Pacchetto dati e riproducibilità",
        "official_url": "https://www.worldbank.org/en/businessready",
        "automated_download": False,
        "authentication_required": False,
        "license": "Indicata nel catalogo World Bank",
        "required": False,
        "status": "not_implemented",
        "coverage_notes": "Quadro regolatorio, servizi pubblici ed efficienza operativa.",
        "limitations": "Copertura internazionale in espansione e metodologia soggetta ad aggiornamenti.",
    },
}

EUROSTAT_EGOVERNMENT_QUERY = {
    "lang": "EN",
    "geo": ["IT", "EU27_2020", "DE", "FR", "ES"],
    "sinceTimePeriod": str(ANALYSIS_START_YEAR),
    "untilTimePeriod": str(ANALYSIS_END_YEAR),
}

PROCEDURE_TYPES = (
    "autorizzazione",
    "comunicazione",
    "concessione",
    "licenza",
    "registrazione",
    "rinnovo",
    "scia",
    "altro",
)

SUBJECT_TYPES = ("impresa", "professionista", "cittadino", "ente", "altro")
OBLIGATION_TYPES = (
    "comunicazione",
    "dichiarazione",
    "domanda",
    "pagamento",
    "registrazione",
    "rinnovo",
    "trasmissione_documenti",
    "altro",
)

TERRITORIAL_LEVELS = (
    "nazionale",
    "regionale",
    "provinciale",
    "citta_metropolitana",
    "comunale",
    "altro",
    "non_classificato",
)

ITALIAN_REGION_NAMES = {
    "01": "Piemonte",
    "02": "Valle d'Aosta/Vallée d'Aoste",
    "03": "Lombardia",
    "04": "Trentino-Alto Adige/Südtirol",
    "05": "Veneto",
    "06": "Friuli-Venezia Giulia",
    "07": "Liguria",
    "08": "Emilia-Romagna",
    "09": "Toscana",
    "10": "Umbria",
    "11": "Marche",
    "12": "Lazio",
    "13": "Abruzzo",
    "14": "Molise",
    "15": "Campania",
    "16": "Puglia",
    "17": "Basilicata",
    "18": "Calabria",
    "19": "Sicilia",
    "20": "Sardegna",
}

LEGAL_OBLIGATION_PATTERNS = {
    "mandatory_action": r"\b(?:è tenut[oa] a|deve presentare|sono tenuti a)\b",
    "deadline": r"\bentro\s+(?:il termine di\s+)?\d+\s+giorn[oi]\b",
    "authorization": r"\bprevia\s+autorizzazione\b",
    "communication": r"\bprevia\s+comunicazione\b",
    "attachment": r"\ballega(?:re|to|ta|ti|te)?\b",
    "frequency": r"\b(?:con cadenza|annualmente|semestralmente|trimestralmente)\b",
    "renewal": r"\brinnovo\b",
    "silence_assent": r"\bsilenzio[- ]assenso\b",
    "sanction": r"\b(?:sanzione|decadenza)\b",
}

SOURCE_INVENTORY_REQUIRED_COLUMNS = (
    "source_id",
    "source_name",
    "institution",
    "source_category",
    "geographical_coverage",
    "time_coverage_start",
    "time_coverage_end",
    "update_frequency",
    "access_method",
    "file_format",
    "official_url",
    "automated_download",
    "authentication_required",
    "license",
    "last_successful_update",
    "status",
    "coverage_notes",
    "limitations",
)

AUTHORITY_REQUIRED_COLUMNS = (
    "authority_id",
    "authority_code",
    "authority_name_original",
    "authority_name_standardized",
    "authority_type",
    "territorial_level",
    "region_code",
    "province_code",
    "municipality_code",
    "website",
    "digital_address",
    "source_id",
    "source_url",
    "retrieved_at",
)

INDICATOR_REQUIRED_COLUMNS = (
    "indicator_id",
    "indicator_name",
    "dimension",
    "territorial_level",
    "territorial_code",
    "territorial_name",
    "reference_period",
    "value",
    "unit",
    "observation_count",
    "source_id",
    "source_url",
    "methodology",
)

TERRITORIAL_COMPARISON_REQUIRED_COLUMNS = (
    "indicator_name",
    "territorial_level",
    "territorial_code",
    "territorial_name",
    "reference_period",
    "value",
    "unit",
    "observation_count",
    "coverage_rate",
    "source_count",
    "quality_flag",
)

QUALITY_MIN_OBSERVATIONS = 30
QUALITY_WARNING_MISSING_SHARE = 0.20
CHART_DPI = 160
CHART_TOP_CATEGORIES = 15
