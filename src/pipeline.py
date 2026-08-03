"""
Punctul unic de orchestrare al pipeline-ului:

    Excel / Google Sheets
            |
            v
       Loaders
            |
            v
    Data Cleaning (processing)
            |
            v
    Business Rules (rules)
            |
            v
    Financial Analysis
            |
            v
          KPIs
            |
            v
        Dashboard

Regula: dashboard.py (ui/) NU apeleaza direct loaders/processing/analysis.
Apeleaza doar functia run_pipeline() de aici si afiseaza rezultatul.
"""

from config.settings import (
    REPORT_FILE,
    CHARGED_SHEET,
    GOOGLE_SHEET_ID,
    GOOGLE_SHEET_TAB,
)
from src.loaders.excel_loader import load_excel
from src.loaders.google_sheet_loader import load_google_sheet
from src.processing.build_clean_jobs import build_clean_jobs_from_df
from src.rules.data_quality import clean_provider_names
from src.analysis.financial_analysis import calculate_financials
from src.analysis.provider_analysis import analyze_providers
from src.models.kpi import calculate_kpis


def load_raw_data():

    try:
        if GOOGLE_SHEET_ID:
            return load_google_sheet(
                GOOGLE_SHEET_ID,
                sheet_name=GOOGLE_SHEET_TAB
            )

    except Exception as e:
        print("Google Sheet failed:", e)
        print("Using local Excel file")


    return load_excel(
        REPORT_FILE,
        CHARGED_SHEET
    )


def run_pipeline():
    """
    Ruleaza intregul pipeline si intoarce un dict cu tot ce are nevoie
    dashboard-ul ca sa afiseze - fara nicio logica de business in ui/.
    """

    raw_df = load_raw_data()

    # Stagiul CLEANING: un singur loc, o singura data.
    jobs_df = build_clean_jobs_from_df(raw_df)

    # Stagiul BUSINESS RULES: un singur loc, o singura data -
    # analizele de mai jos primesc deja date curate, nu mai aplica reguli.
    jobs_df = clean_provider_names(jobs_df)

    # Stagiul FINANCIAL ANALYSIS + KPIs + provider breakdown.
    financials = calculate_financials(jobs_df)
    kpis = calculate_kpis(jobs_df)
    provider_df = analyze_providers(jobs_df)

    return {
        "jobs_df": jobs_df,
        "financials": financials,
        "kpis": kpis,
        "provider_df": provider_df,
        "source": "Google Sheets" if GOOGLE_SHEET_ID else "fisier local",
    }
