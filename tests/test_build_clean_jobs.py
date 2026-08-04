import pandas as pd

from src.processing.build_clean_jobs import build_clean_jobs_from_df


def _sample_df():
    return pd.DataFrame({
        "Job #": ["GA-1001", "GA-1001", "FB-1002", "FB-1002", "RF-9999"],
        "Customer Name": ["A", "A", "B", "B (repeat)", "C"],
        "Source": ["Google Ads"] * 5,
        "Date": [
            "2026-07-10", "2026-07-13",
            "2026-07-17", "2026-07-22",
            None,
        ],
        "Status": ["quoted", "booked", "won", "repeat_payment", "new_lead"],
        "Charged": [0, 630, 1076.25, 341.25, 0],
        "Deposit": [525, 75, 0, 0, 100],
        "Cost": [40.32, 0, 0, 0, 30],
    })


def test_dedup_keeps_one_row_per_job():
    result = build_clean_jobs_from_df(_sample_df())
    assert result["Job #"].nunique() == len(result) == 3


def test_charged_is_summed_across_all_rows_of_a_job():
    result = build_clean_jobs_from_df(_sample_df())
    ga = result.loc[result["Job #"] == "GA-1001", "Charged"].iloc[0]
    fb = result.loc[result["Job #"] == "FB-1002", "Charged"].iloc[0]
    assert ga == 630
    assert fb == 1076.25 + 341.25


def test_last_row_keeps_final_status_not_a_mixed_row():
    result = build_clean_jobs_from_df(_sample_df())
    fb_status = result.loc[result["Job #"] == "FB-1002", "Status"].iloc[0]
    assert fb_status == "repeat_payment"


def test_row_with_missing_date_does_not_become_the_final_row():
    df = pd.DataFrame({
        "Job #": ["X-1", "X-1"],
        "Customer Name": ["x", "x"],
        "Source": ["Google Ads", "Google Ads"],
        "Date": [None, "2026-07-05"],
        "Status": ["missing_date_row", "real_last_status"],
        "Charged": [0, 500],
        "Deposit": [0, 0],
        "Cost": [0, 0],
    })
    result = build_clean_jobs_from_df(df)
    assert result["Status"].iloc[0] == "real_last_status"


def test_margin_is_zero_when_no_charge():
    result = build_clean_jobs_from_df(_sample_df())
    rf = result.loc[result["Job #"] == "RF-9999"].iloc[0]
    assert rf["Charged"] == 0
    assert rf["Margin %"] == 0
