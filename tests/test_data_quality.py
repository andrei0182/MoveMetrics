import pandas as pd

from src.rules.data_quality import clean_provider_names, data_quality_report


def test_real_source_names_are_not_blanked():
    df = pd.DataFrame({
        "Job #": ["GA-1001", "FB-1002", "RF-1003"],
        "Source": ["Google Ads", "Facebook Ads", "Referral"],
        "Charged": [840, 1128.75, 840],
    })
    result = clean_provider_names(df)
    assert "unknown" not in result["Source"].values


def test_shifted_row_where_source_is_actually_a_job_id_is_flagged():
    df = pd.DataFrame({
        "Job #": ["GA-1001", "GA-1002"],
        "Source": ["Google Ads", "GA-1500"],
        "Charged": [500, 300],
    })
    result = clean_provider_names(df)
    assert result.loc[result["Job #"] == "GA-1002", "Source"].iloc[0] == "unknown"


def test_missing_source_column_is_a_noop():
    df = pd.DataFrame({"Job #": ["A"], "Charged": [100]})
    result = clean_provider_names(df)
    assert "Source" not in result.columns


def test_data_quality_report_counts_suspicious_source():
    df = pd.DataFrame({
        "Job #": ["GA-1001", "GA-1002"],
        "Source": ["Google Ads", "GA-1500"],
    })
    report = data_quality_report(df)
    assert report["Suspicious Source (looks like a Job ID)"] == 1
