# PFM-Analytics-Suite

Dashboard de business intelligence pentru "Perfectly Fast Moving" (PFM) — proceseaza
raportul zilnic de leaduri/joburi si calculeaza revenue, cost, profit si performanta
pe sursa de leaduri.

## Instalare

```bash
pip install -r requirements.txt
```

## Date de intrare

Pune raportul zilnic (`Report_JUL.xlsx`, cu sheet-ul consolidat `CHARGED`) in:

```
data/raw/Report_JUL.xlsx
```

Acest folder e in `.gitignore` — datele de client nu se comit niciodata in repo.
Calea si numele sheet-ului sunt centralizate in `config/settings.py`.

## Rulare dashboard

```bash
streamlit run app.py
```

## Pipeline de date

`src/processing/build_clean_jobs.py` transforma raportul brut (mai multe randuri
per Job #, cate unul pentru fiecare eveniment — lead nou, quoted, booked, plata
ulterioara pe job vechi) intr-un singur rand per Job #, cu:

- ultimul status real inregistrat pe job
- suma tuturor incasarilor (Charged) pe toata durata jobului
- costul total pe job, profit, marja

Toate modulele de analiza (`kpi.py`, `provider_analysis.py`) opereaza pe acest
rezultat deduplicat, nu pe raportul brut.

## Teste

```bash
pytest tests/ -v
```
