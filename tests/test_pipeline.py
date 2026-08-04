import pandas as pd
from unittest.mock import patch

from src.pipeline import run_pipeline


def _fake_raw_df():
    return pd.DataFrame({
        "Job #": ["GA-1001", "WB-9999"],
        "Customer Name": ["a", "b"],
        "Source": ["Google Ads", "Website"],
        "Date": ["2026-07-09", "2026-07-10"],
        "Status": ["booked", "booked"],
        "Charged": [840, 500],
        "Deposit": [800, 500],
        "Cost": [22.62, 10],
    })


@patch("src.pipeline.GOOGLE_SHEET_ID", None)
@patch("src.pipeline.USE_OWN_DATA", True)
@patch("src.pipeline.load_excel")
def test_pipeline_runs_all_stages_in_order(mock_load_excel):
    mock_load_excel.return_value = _fake_raw_df()

    result = run_pipeline()

    assert len(result["jobs_df"]) == 2

    ga_source = result["jobs_df"].loc[
        result["jobs_df"]["Job #"] == "GA-1001", "Source"
    ].iloc[0]
    assert ga_source == "Google Ads"

    assert result["financials"]["Revenue"] == 1340
    assert result["kpis"]["Total Jobs"] == 2
    assert set(result["provider_df"]["Source"]) == {"Google Ads", "Website"}
    assert result["source"] == "your data (local file)"

    assert result["lead_funnel"]["Total Leads"] == 2
    assert result["lead_funnel"]["Converted"] == 2
    assert result["lead_funnel"]["Conversion Rate %"] == 100.0


@patch("src.pipeline.GOOGLE_SHEET_ID", None)
@patch("src.pipeline.USE_OWN_DATA", True)
@patch("src.pipeline.load_excel")
def test_lead_funnel_by_source_matches_provider_profit_order(mock_load_excel):
    mock_load_excel.return_value = pd.DataFrame({
        "Job #": ["A", "B", "C", "D"],
        "Customer Name": ["x", "y", "z", "w"],
        "Source": ["Google Ads", "Facebook Ads", "Referral", "Website"],
        "Date": ["2026-07-01"] * 4,
        "Status": ["booked"] * 4,
        "Charged": [500, 100, 600, 200],
        "Deposit": [0, 0, 0, 0],
        "Cost": [50, 300, 10, 0],
    })

    result = run_pipeline()

    provider_order = result["provider_df"]["Source"].tolist()
    by_source_order = result["lead_funnel"]["by_source"]["Source"].tolist()

    assert provider_order == by_source_order
    assert provider_order[0] == "Referral"       # profit 590, highest
    assert provider_order[-1] == "Facebook Ads"  # profit -200, a loss
    assert result["profit_order"] == provider_order


@patch("src.pipeline.GOOGLE_SHEET_ID", "fake_sheet_id")
@patch("src.pipeline.GOOGLE_SHEET_TAB", "LEADS")
@patch("src.pipeline.load_google_sheet")
def test_pipeline_uses_google_sheets_when_configured(mock_load_sheet):
    mock_load_sheet.return_value = _fake_raw_df()

    result = run_pipeline()

    mock_load_sheet.assert_called_once_with("fake_sheet_id", sheet_name="LEADS")
    assert result["source"] == "Google Sheets"


@patch("src.pipeline.GOOGLE_SHEET_ID", None)
@patch("src.pipeline.USE_OWN_DATA", False)
@patch("src.pipeline.load_excel")
def test_pipeline_defaults_to_demo_file(mock_load_excel):
    mock_load_excel.return_value = _fake_raw_df()

    result = run_pipeline()

    assert result["source"] == "synthetic demo data"
