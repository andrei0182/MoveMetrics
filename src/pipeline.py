"""
Single orchestration entry point for the pipeline:

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

Rule: dashboard.py (ui/) never calls loaders/processing/analysis directly.
It calls run_pipeline() here and only renders the result.
"""

import pandas as pd

from config.settings import (
    DEMO_FILE,
    REPORT_FILE,
    USE_OWN_DATA,
    LEADS_SHEET_NAME,
    GOOGLE_SHEET_ID,
    GOOGLE_SHEET_TAB,
)
from src.loaders.excel_loader import load_excel
from src.loaders.google_sheet_loader import load_google_sheet
from src.processing.build_clean_jobs import build_clean_jobs_from_df
from src.rules.data_quality import clean_provider_names
from src.analysis.financial_analysis import calculate_financials
from src.analysis.provider_analysis import analyze_providers
from src.analysis.lead_analysis import analyze_leads
from src.models.kpi import calculate_kpis


def load_raw_data():
    """
    LOADERS stage. Priority:
    1. Google Sheets, if GOOGLE_SHEET_ID is set
    2. Your own local file, if USE_OWN_DATA is True
    3. The bundled synthetic demo file (default - works with zero setup)
    """

    if GOOGLE_SHEET_ID:
        return load_google_sheet(GOOGLE_SHEET_ID, sheet_name=GOOGLE_SHEET_TAB)

    if USE_OWN_DATA:
        return load_excel(REPORT_FILE, LEADS_SHEET_NAME)

    return load_excel(DEMO_FILE, LEADS_SHEET_NAME)


def run_pipeline():
    """Runs the full pipeline and returns everything the dashboard needs
    to render - no business logic lives in ui/."""

    raw_df = load_raw_data()

    # CLEANING stage: one place, once.
    jobs_df = build_clean_jobs_from_df(raw_df)

    # BUSINESS RULES stage: one place, once - analyses below receive
    # already-clean data and don't re-apply rules themselves.
    jobs_df = clean_provider_names(jobs_df)

    # FINANCIAL ANALYSIS + KPIs + provider breakdown + lead funnel.
    financials = calculate_financials(jobs_df)
    kpis = calculate_kpis(jobs_df)
    provider_df = analyze_providers(jobs_df)
    lead_funnel = analyze_leads(jobs_df)

    # Visual consistency: the same profitability order (from provider_df,
    # already sorted by Profit descending) is applied to lead_funnel's
    # by_source table too, so every chart/table in the dashboard shows
    # sources in the same order instead of each picking its own.
    profit_order = provider_df["Source"].tolist()
    by_source = lead_funnel["by_source"].copy()
    by_source["Source"] = pd.Categorical(
        by_source["Source"], categories=profit_order, ordered=True
    )
    lead_funnel["by_source"] = by_source.sort_values("Source").reset_index(drop=True)

    if GOOGLE_SHEET_ID:
        source_label = "Google Sheets"
    elif USE_OWN_DATA:
        source_label = "your data (local file)"
    else:
        source_label = "synthetic demo data"

    return {
        "jobs_df": jobs_df,
        "financials": financials,
        "kpis": kpis,
        "provider_df": provider_df,
        "lead_funnel": lead_funnel,
        "profit_order": profit_order,
        "source": source_label,
    }
