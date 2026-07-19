# Burocrazia italiana

Repository per raccogliere, pulire, integrare e analizzare dati relativi alla burocrazia italiana. Il progetto separa fonti, trasformazioni, indicatori, controlli di qualità e grafici, così ogni risultato può essere ricondotto al dato originario e replicato con la stessa configurazione.

La prima versione concentra il lavoro sulle attività economiche e sulle amministrazioni pubbliche. La struttura è predisposta per integrare in seguito procedimenti rivolti a cittadini, professionisti ed enti.

## Obiettivo del progetto

Il progetto serve a costruire una base dati verificabile su questi aspetti:

- atti e disposizioni normative;
- procedimenti amministrativi;
- adempimenti richiesti a imprese e cittadini;
- documenti, moduli, firme e pagamenti richiesti;
- amministrazioni coinvolte;
- costi e tempi previsti;
- tempi osservati, quando disponibili;
- possibilità di completare un procedimento online;
- differenze territoriali;
- frequenza delle modifiche normative;
- indicatori nazionali e internazionali sul contesto regolatorio e digitale.

Il repository non assume che esista una singola misura esaustiva della burocrazia. Mantiene separate le dimensioni osservabili e documenta la copertura di ogni fonte.

## Domande di ricerca

Il progetto è impostato per rispondere progressivamente a domande come queste:

1. Quali passaggi, documenti, costi e amministrazioni caratterizzano un procedimento?
2. Quanto differiscono termini, costi e modalità di presentazione tra territori?
3. Quale quota dei procedimenti può essere completata interamente online?
4. Quanto spesso cambiano le disposizioni che regolano uno stesso adempimento?
5. Qual è la differenza tra termine legale e tempo effettivamente osservato?
6. Quali informazioni richieste sono già detenute da una pubblica amministrazione?
7. Quali fonti permettono confronti nazionali, territoriali e internazionali affidabili?

## Perimetro dell'analisi

La prima versione considera soprattutto la burocrazia collegata alle attività economiche. Gli eventi di interesse comprendono:

- costituzione di un'impresa;
- avvio di un'attività;
- apertura di una sede;
- assunzione del primo dipendente;
- richiesta di un'autorizzazione;
- presentazione di una SCIA;
- partecipazione a una gara pubblica;
- rinnovo di una licenza o concessione;
- cessazione di un'attività.

La copertura effettiva dipende dalle fonti già integrate. Nello stato iniziale il repository acquisisce l'anagrafica degli enti IPA e un dataset Eurostat sull'uso dei servizi pubblici online. Le fonti normative e i cataloghi dei procedimenti sono censiti nell'inventario e richiedono connettori successivi.

## Definizioni

**Quantità di norme** indica il numero di atti o disposizioni in un determinato perimetro. Un numero elevato di atti non dimostra da solo un carico amministrativo elevato.

**Complessità normativa** riguarda modifiche, rinvii, stratificazione, atti attuativi e difficoltà di ricostruzione della disciplina applicabile.

**Complessità procedurale** riguarda il numero di passaggi, documenti, amministrazioni, moduli, firme, pagamenti e canali necessari per completare un procedimento.

**Costo amministrativo** comprende diritti, bolli, costi professionali e tempo di lavoro impiegato per adempiere.

**Tempo amministrativo** può indicare un termine previsto dalla norma o un tempo osservato. I due valori devono rimanere distinti.

**Digitalizzazione** descrive singole funzioni online e la possibilità di completare l'intero procedimento in formato digitale. La presenza di un modulo scaricabile non implica un procedimento end-to-end digitale.

**Variabilità territoriale** misura differenze tra territori riferite allo stesso procedimento e allo stesso periodo, dopo aver verificato la comparabilità.

**Percezione della burocrazia** deriva da indagini presso cittadini o imprese. Non rappresenta una misura diretta di costi, documenti o tempi.

## Struttura del repository

```text
Burocrazia_Italiana/
  README.md
  requirements.txt

  scripts/
    config.py
    utils.py
    src/
      download_legal_data.py
      download_administrative_data.py
      download_statistical_data.py
      build_source_inventory.py
      clean_legal_data.py
      clean_administrative_data.py
      build_bureaucracy_indicators.py
      build_territorial_comparisons.py
      check_data_quality.py
      make_bureaucracy_charts.py
      run_pipeline.py

  notebooks/
    01_source_inventory_and_data_check.ipynb
    02_legal_complexity_analysis.ipynb
    03_administrative_procedures_analysis.ipynb
    04_territorial_comparison.ipynb
    05_final_outputs.ipynb

  output/
    data/
      raw/
      clean/
      processed/
      quality/
    charts/
      legal_complexity/
      administrative_procedures/
      territorial_comparisons/
      international_comparisons/
```

`scripts/config.py` contiene percorsi, URL, anni, nomi dei file, classificazioni, soglie e parametri. Percorsi e costanti non devono essere duplicati nei notebook.

`scripts/utils.py` contiene funzioni generali per download, lettura e salvataggio, normalizzazione, identificatori, hash, validazione e conversione JSON-stat.

`scripts/src` contiene il codice operativo. Ogni file ha una responsabilità specifica.

`notebooks` contiene analisi ed esplorazioni ordinate secondo la sequenza del progetto. I notebook richiamano le funzioni presenti in `scripts` e non duplicano la pipeline.

`output/data/raw` conserva le risposte e i file originari senza trasformazioni.

`output/data/clean` contiene dati standardizzati a livello di singola fonte.

`output/data/processed` contiene inventari, indicatori e confronti pronti per l'analisi.

`output/data/quality` contiene i report dei controlli automatici.

`output/charts` contiene esclusivamente grafici e immagini generati dal codice.

I file prodotti nella cartella `output` sono esclusi dalla cronologia Git. I file `.gitkeep` conservano la struttura delle cartelle.

## Fonti dei dati

### Fonti implementate

| Fonte | Contenuto | Accesso | Uso nel repository |
|---|---|---|---|
| [Indice delle Pubbliche Amministrazioni - Enti](https://indicepa.gov.it/ipa-dati/dataset/enti) | Anagrafica degli enti, tipologia, sede, sito e recapiti | Download XLSX ufficiale | Anagrafica delle amministrazioni, indicatori di copertura e confronti per regione della sede |
| [Eurostat - Data access via API](https://ec.europa.eu/eurostat/data/web-services) | Dataset `isoc_ciegi_ac` sull'uso dei servizi pubblici online | API REST, JSON-stat 2.0 | Indicatori di contesto digitale per Italia, UE e paesi selezionati |

Il dataset IPA è pubblicato con licenza CC BY 4.0. Le condizioni di riuso Eurostat sono indicate sul portale istituzionale.

### Fonti censite e non ancora integrate

L'inventario iniziale comprende anche:

- [Normattiva Open Data](https://dati.normattiva.it/);
- [Gazzetta Ufficiale](https://www.gazzettaufficiale.it/);
- [EUR-Lex](https://eur-lex.europa.eu/);
- [dati.gov.it](https://www.dati.gov.it/);
- [Catalogo del Sistema degli Sportelli Unici](https://catalogo.impresainungiorno.gov.it/);
- [ANAC Open Data](https://dati.anticorruzione.it/);
- [IstatData](https://esploradati.istat.it/);
- [OECD Product Market Regulation](https://www.oecd.org/en/topics/product-market-regulation.html);
- [World Bank Business Ready](https://www.worldbank.org/en/businessready).

Una fonte non implementata rimane nell'inventario con stato `not_implemented` o `manual_only`. Il codice non crea risposte simulate.

## Installazione

È consigliato Python 3.11 o successivo.

Creare un ambiente virtuale:

```bash
python -m venv .venv
```

Su Linux o macOS:

```bash
source .venv/bin/activate
```

Su Windows:

```bash
.venv\Scripts\activate
```

Installare le dipendenze:

```bash
pip install -r requirements.txt
```

## Esecuzione della pipeline

Dalla cartella principale del repository:

```bash
python scripts/src/run_pipeline.py
```

La pipeline esegue questi passaggi:

1. crea le cartelle di output;
2. costruisce l'inventario iniziale delle fonti;
3. registra lo stato dei connettori normativi;
4. scarica il dataset IPA Enti;
5. prova a scaricare il dataset Eurostat opzionale;
6. prepara le tabelle normative con schema stabile;
7. pulisce l'anagrafica IPA;
8. costruisce indicatori elementari;
9. costruisce confronti territoriali descrittivi;
10. aggiorna l'inventario con gli esiti dei download;
11. esegue i controlli di qualità e genera i grafici.

Il dataset IPA è una fonte obbligatoria nella prima versione. Un errore di download interrompe la pipeline. Eurostat è una fonte opzionale; un'indisponibilità temporanea viene registrata e la pipeline prosegue con gli altri dati.

Per forzare un nuovo download modificare in `scripts/config.py`:

```python
FORCE_DOWNLOAD = True
```

Ripristinare il valore a `False` dopo l'aggiornamento. Con `False`, i file recenti vengono riutilizzati secondo `MAX_FILE_AGE_DAYS`.

### Esecuzione dei singoli passaggi

```bash
python scripts/src/build_source_inventory.py
python scripts/src/download_legal_data.py
python scripts/src/download_administrative_data.py
python scripts/src/download_statistical_data.py
python scripts/src/clean_legal_data.py
python scripts/src/clean_administrative_data.py
python scripts/src/build_bureaucracy_indicators.py
python scripts/src/build_territorial_comparisons.py
python scripts/src/check_data_quality.py
python scripts/src/make_bureaucracy_charts.py
```

## Utilizzo dei notebook

Avviare Jupyter dalla cartella principale:

```bash
jupyter notebook
```

La sequenza consigliata è:

1. `01_source_inventory_and_data_check.ipynb` per verificare fonti, file e qualità;
2. `02_legal_complexity_analysis.ipynb` per preparare l'analisi normativa;
3. `03_administrative_procedures_analysis.ipynb` per analizzare amministrazioni e, in seguito, procedimenti;
4. `04_territorial_comparison.ipynb` per confronti regionali con indicatori di copertura;
5. `05_final_outputs.ipynb` per produrre tabelle, controlli e grafici finali.

I notebook non contengono percorsi di output scritti direttamente. Importano le configurazioni e le funzioni del progetto.

## Dataset prodotti

### `output/data/processed/source_inventory.csv`

Unità di osservazione: fonte.

Contiene istituzione, categoria, copertura, frequenza, metodo di accesso, formato, licenza, stato, ultimo aggiornamento riuscito e limitazioni.

### `output/data/clean/authorities.parquet`

Unità di osservazione: ente presente in IPA.

Colonne principali:

- `authority_id`;
- `authority_code`;
- `authority_name_original`;
- `authority_name_standardized`;
- `authority_type`;
- `territorial_level`;
- `region_code`;
- `province_code`;
- `municipality_code`;
- `website`;
- `digital_address`;
- `source_id`;
- `source_url`;
- `retrieved_at`.

La versione CSV è salvata in `output/data/clean/authorities.csv`.

### `output/data/clean/legal_acts.parquet`

Unità di osservazione prevista: atto normativo.

Nella prima versione la tabella è vuota perché il connettore Normattiva non è ancora implementato. Lo schema è già disponibile per evitare modifiche incompatibili nei passaggi successivi.

### `output/data/clean/legal_provisions.parquet`

Unità di osservazione prevista: articolo, comma, lettera o altra disposizione.

La tabella include flag trasparenti per selezionare possibili obblighi, termini, rinnovi e sanzioni. I flag non identificano automaticamente un onere burocratico.

### `output/data/clean/administrative_procedures.parquet`

Unità di osservazione prevista: procedimento amministrativo.

La tabella iniziale è vuota. Verrà popolata con cataloghi SUAP, SUE e altre fonti ufficiali.

### `output/data/clean/eurostat_egovernment_long.parquet`

Unità di osservazione: cella non nulla del dataset JSON-stat Eurostat.

Il file conserva codici ed etichette delle dimensioni originarie.

### `output/data/processed/bureaucracy_indicators.parquet`

Unità di osservazione: indicatore, territorio, periodo e breakdown.

Contiene indicatori descrittivi sull'anagrafica IPA e indicatori Eurostat di contesto digitale. La versione CSV è salvata nello stesso percorso con estensione `.csv`.

### `output/data/processed/territorial_comparisons.parquet`

Unità di osservazione: indicatore e regione.

La prima versione confronta numerosità e disponibilità di recapiti IPA per regione della sede. La versione CSV è salvata nello stesso percorso.

### `output/data/quality/data_quality_report.csv`

Unità di osservazione: controllo applicato a un dataset.

Contiene stato, righe interessate, quota interessata, severità, descrizione e data di generazione.

## Grafici prodotti

Quando i dati necessari sono disponibili, il codice produce:

- `output/charts/administrative_procedures/ipa_authorities_by_type.png`;
- `output/charts/territorial_comparisons/ipa_digital_address_by_region.png`;
- `output/charts/international_comparisons/eurostat_egovernment_comparison.png`.

Ogni grafico riporta fonte e nota interpretativa. I titoli descrivono il contenuto senza attribuire relazioni causali.

## Metodologia

### Acquisizione

La priorità delle modalità di accesso è:

1. API ufficiale;
2. file strutturato ufficiale;
3. catalogo open data;
4. pagina HTML strutturata;
5. documento PDF;
6. importazione manuale documentata.

Ogni download salva, quando disponibile:

- fonte;
- URL richiesto e URL risolto;
- data e ora UTC;
- stato HTTP;
- tipo di contenuto;
- dimensione del file;
- hash SHA-256;
- ETag e data di ultima modifica comunicati dal server.

I dati grezzi non vengono sovrascritti con dati puliti.

### Standardizzazione delle amministrazioni

Il codice conserva la denominazione originale IPA e crea una denominazione standardizzata per i confronti. La normalizzazione uniforma Unicode, spazi, maiuscole e punteggiatura. Le forme giuridiche non vengono eliminate.

`authority_id` è deterministico e deriva da codice IPA e denominazione standardizzata. Non dipende dall'ordine delle righe.

Il livello territoriale è una classificazione operativa ottenuta da tipologia e denominazione. Non è una classificazione ufficiale delle competenze.

`region_code` e `province_code` derivano dal codice ISTAT del comune sede. La sede non rappresenta necessariamente l'area di competenza dell'ente.

### Indicatori IPA

Gli indicatori iniziali misurano:

- numero di record IPA;
- quota di record con sito istituzionale;
- quota di record con un recapito digitale valorizzato.

Questi indicatori descrivono l'anagrafica e la disponibilità dei campi. Non misurano la qualità del servizio, la capacità amministrativa o l'onere sostenuto da imprese e cittadini.

### Indicatori Eurostat

Il codice acquisisce il dataset `isoc_ciegi_ac` in JSON-stat 2.0 e lo converte in formato lungo. I valori riguardano l'uso dei servizi pubblici online da parte degli individui.

Questi dati costituiscono un indicatore di contesto. Non sostituiscono misure dirette di passaggi, documenti, costi o tempi.

### Selezione di disposizioni normative

Le espressioni regolari presenti in `scripts/config.py` servono a selezionare disposizioni potenzialmente rilevanti per una revisione manuale. La presenza di termini come “autorizzazione”, “rinnovo” o “sanzione” non determina da sola l'esistenza o l'entità di un onere.

### Confronti territoriali

Un confronto viene accompagnato da:

- numero di osservazioni;
- quota di copertura;
- numero di fonti;
- flag di qualità.

La soglia minima iniziale è definita in `QUALITY_MIN_OBSERVATIONS`. I territori con numerosità insufficiente non devono essere usati per classifiche.

### Indici compositi

La prima versione non costruisce un indice sintetico unico. Un indice composito richiederebbe copertura sufficiente, pesi espliciti, normalizzazione documentata e analisi di sensibilità. Gli indicatori elementari resterebbero comunque disponibili.

## Controlli di qualità

Il report automatico verifica almeno:

- presenza dei file;
- colonne obbligatorie;
- chiavi duplicate;
- stati delle fonti ammessi;
- valori mancanti in campi selezionati;
- numerosità non negative;
- copertura compresa tra zero e uno.

I controlli non eliminano record. Un valore estremo viene segnalato e richiede valutazione metodologica. Il codice distingue tra valore mancante e zero.

## Assunzioni

1. Il codice IPA identifica stabilmente un ente nel perimetro del dataset.
2. Le prime due cifre del codice ISTAT comunale identificano la regione e le prime tre la provincia.
3. Il campo `Sito_istituzionale` valorizzato indica disponibilità del recapito nel registro, senza verifica automatica della raggiungibilità.
4. Un indirizzo classificato come PEC ha priorità nella costruzione di `digital_address`; in assenza di PEC viene conservata la prima e-mail disponibile.
5. Il periodo dell'indicatore IPA deriva dalla data di acquisizione o dalla data di aggiornamento disponibile nella fonte.
6. Le osservazioni Eurostat vengono mantenute nella struttura originaria delle dimensioni e non vengono aggregate nel codice iniziale.

## Limitazioni

- Non esiste ancora un catalogo integrato dei procedimenti amministrativi.
- Il connettore Normattiva non è implementato.
- Tempi effettivi, richieste di integrazione ed esiti non sono disponibili nella prima versione.
- Costi professionali e ore di lavoro richiedono dati amministrativi o indagini specifiche.
- Le informazioni IPA descrivono il registro degli enti e non le prestazioni amministrative.
- La regione della sede non coincide sempre con il territorio di competenza.
- Eurostat misura comportamenti e utilizzo dei servizi digitali, non l'onere burocratico diretto.
- La copertura delle fonti locali può variare nel tempo e tra territori.
- Le fonti online possono modificare struttura, URL e modalità di accesso.

## Interpretazione dei risultati

Leggere ogni indicatore insieme a fonte, periodo, unità, osservazioni e copertura.

Un valore elevato del numero di enti in una regione può dipendere dalla struttura istituzionale e dalla localizzazione delle sedi. Non dimostra una maggiore burocrazia.

Una quota elevata di recapiti digitali indica una maggiore completezza del campo IPA. Non dimostra che i procedimenti siano interamente digitali.

Un aumento dell'uso dei servizi pubblici online può dipendere da offerta digitale, competenze, obblighi di utilizzo, struttura demografica e qualità dei servizi. Il dato non identifica da solo il meccanismo causale.

I confronti territoriali devono essere limitati a definizioni e periodi omogenei. I valori mancanti non devono essere interpretati come zero.

## Aggiornamento dei dati

Per aggiornare tutte le fonti implementate:

1. impostare `FORCE_DOWNLOAD = True` in `scripts/config.py`;
2. eseguire `python scripts/src/run_pipeline.py`;
3. controllare `output/data/quality/data_quality_report.csv`;
4. verificare le variazioni anomale rispetto all'esecuzione precedente;
5. ripristinare `FORCE_DOWNLOAD = False`.

Prima di pubblicare risultati aggiornati, controllare che la fonte non abbia modificato colonne, definizioni o licenza.

## Come aggiungere una nuova fonte

1. Inserire la fonte in `DATA_SOURCES` dentro `scripts/config.py`.
2. Documentare istituzione, copertura, frequenza, accesso, formato, licenza e limitazioni.
3. Verificare l'endpoint o il download sulla documentazione ufficiale.
4. Aggiungere una funzione di acquisizione nel file operativo pertinente.
5. Salvare il contenuto originario in `output/data/raw`.
6. Salvare un manifest con URL, data, hash e metodo di estrazione.
7. Aggiungere la pulizia senza modificare il file grezzo.
8. Conservare valori originali e standardizzati.
9. Aggiungere controlli di qualità e testare colonne e chiavi.
10. Aggiornare README, inventario, notebook e grafici pertinenti.

Non inserire endpoint ipotetici, dati fittizi o risultati simulati.

## Licenze e condizioni d'uso

Il codice del repository deve essere accompagnato da una licenza scelta dal titolare del progetto. I dati mantengono le licenze e le condizioni d'uso delle fonti originarie.

La presenza di un URL pubblico non implica automaticamente libertà di riuso. Prima di redistribuire dati o estratti verificare licenza, attribuzione richiesta, condizioni tecniche e limiti della fonte.
