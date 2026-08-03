import pandas as pd

from src.rules.data_quality import clean_provider_names, data_quality_report


def test_real_job_ids_are_not_blanked_to_unknown():
    # Regresie: AL4170, AL4470 si WB1031-DUP sunt joburi booked reale,
    # cu Sursa reala - o lista hardcodata veche le stergea gresit.
    df = pd.DataFrame({
        "Job #": ["AL4170", "AL4470", "WB1031-DUP"],
        "Sursa": ["angieslist", "angieslist", "website"],
        "Charged": [840, 1128.75, 840],
    })
    result = clean_provider_names(df)
    assert "unknown" not in result["Sursa"].values
    assert set(result["Sursa"]) == {"angieslist", "website"}


def test_shifted_row_where_sursa_is_actually_a_job_id_is_flagged():
    df = pd.DataFrame({
        "Job #": ["AL1", "AL2"],
        "Sursa": ["angieslist", "AL4993"],
        "Charged": [500, 300],
    })
    result = clean_provider_names(df)
    assert result.loc[result["Job #"] == "AL2", "Sursa"].iloc[0] == "unknown"


def test_missing_sursa_column_is_a_noop():
    df = pd.DataFrame({"Job #": ["A"], "Charged": [100]})
    result = clean_provider_names(df)
    assert "Sursa" not in result.columns


def test_data_quality_report_counts_suspicious_sursa():
    df = pd.DataFrame({
        "Job #": ["AL1", "AL2"],
        "Sursa": ["angieslist", "AL4993"],
    })
    report = data_quality_report(df)
    assert report["Suspicious Sursa (arata ca Job #)"] == 1
