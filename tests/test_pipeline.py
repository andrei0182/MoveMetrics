import pandas as pd
from unittest.mock import patch

from src.pipeline import run_pipeline


def _fake_raw_df():
    # AL4170 e in lista veche hardcodata (eliminata) - daca pipeline-ul
    # aplica regulile de business (Stagiul 3) INAINTE de analiza
    # (Stagiul 4), Sursa lui trebuie sa ramana "angieslist", nu "unknown".
    return pd.DataFrame({
        "Job #": ["AL4170", "AL9999"],
        "Nume Client": ["a", "b"],
        "Sursa": ["angieslist", "website"],
        "Data": ["2026-07-09", "2026-07-10"],
        "Status": ["booked", "booked"],
        "Charged": [840, 500],
        "Deposit": [800, 500],
        "Cost": [22.62, 10],
    })


@patch("src.pipeline.GOOGLE_SHEET_ID", None)
@patch("src.pipeline.load_excel")
def test_pipeline_runs_all_stages_in_order(mock_load_excel):
    mock_load_excel.return_value = _fake_raw_df()

    result = run_pipeline()

    # Stagiul cleaning: un rand per job.
    assert len(result["jobs_df"]) == 2

    # Stagiul business rules aplicat inainte de analiza:
    # AL4170 (fost in lista hardcodata veche) trebuie sa-si pastreze Sursa reala.
    al4170_sursa = result["jobs_df"].loc[
        result["jobs_df"]["Job #"] == "AL4170", "Sursa"
    ].iloc[0]
    assert al4170_sursa == "angieslist"

    # Stagiile financial analysis + KPIs + provider produc rezultate coerente.
    assert result["financials"]["Revenue"] == 1340
    assert result["kpis"]["Total Jobs"] == 2
    assert set(result["provider_df"]["Sursa"]) == {"angieslist", "website"}
    assert result["source"] == "fisier local"

    # Stagiul lead funnel: ambele joburi sunt "leaduri", ambele au Charged>0.
    assert result["lead_funnel"]["Total Leads"] == 2
    assert result["lead_funnel"]["Converted"] == 2
    assert result["lead_funnel"]["Conversion Rate %"] == 100.0


@patch("src.pipeline.GOOGLE_SHEET_ID", None)
@patch("src.pipeline.load_excel")
def test_lead_funnel_by_source_matches_provider_profit_order(mock_load_excel):
    # 4 surse, profitabilitate foarte diferita - trebuie ca ambele tabele
    # sa arate sursele in ACEEASI ordine (Profit descrescator), nu fiecare
    # in ordinea ei implicita (alfabetica pentru by_source, altfel pt provider).
    mock_load_excel.return_value = pd.DataFrame({
        "Job #": ["A", "B", "C", "D"],
        "Nume Client": ["x", "y", "z", "w"],
        "Sursa": ["angieslist", "allpoint_media", "manual", "website"],
        "Data": ["2026-07-01"] * 4,
        "Status": ["booked"] * 4,
        "Charged": [500, 100, 600, 200],
        "Deposit": [0, 0, 0, 0],
        "Cost": [50, 300, 10, 0],
    })

    result = run_pipeline()

    provider_order = result["provider_df"]["Sursa"].tolist()
    by_source_order = result["lead_funnel"]["by_source"]["Sursa"].tolist()

    assert provider_order == by_source_order
    assert provider_order[0] == "manual"       # profit 590, cel mai mare
    assert provider_order[-1] == "allpoint_media"  # profit -200, pierdere


@patch("src.pipeline.GOOGLE_SHEET_ID", "fake_sheet_id")
@patch("src.pipeline.GOOGLE_SHEET_TAB", "CHARGED")
@patch("src.pipeline.load_google_sheet")
def test_pipeline_uses_google_sheets_when_configured(mock_load_sheet):
    mock_load_sheet.return_value = _fake_raw_df()

    result = run_pipeline()

    mock_load_sheet.assert_called_once_with("fake_sheet_id", sheet_name="CHARGED")
    assert result["source"] == "Google Sheets"