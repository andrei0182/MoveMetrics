import pandas as pd

from src.analysis.provider_analysis import analyze_providers


def test_jobs_count_is_nunique_not_row_count():
    # Doua randuri, un singur Job # -> Jobs trebuie sa fie 1, nu 2.
    jobs_df = pd.DataFrame({
        "Job #": ["A", "A"],
        "Sursa": ["angieslist", "angieslist"],
        "Charged": [500, 500],
    })
    result = analyze_providers(jobs_df)
    assert result.loc[result["Sursa"] == "angieslist", "Jobs"].iloc[0] == 1


def test_real_job_ids_are_not_blanked_to_unknown():
    # Regresie pentru bug-ul cu lista hardcodata: AL4170, AL4470 si
    # WB1031-DUP sunt joburi reale cu Sursa reala - nu trebuie sterse.
    jobs_df = pd.DataFrame({
        "Job #": ["AL4170", "AL4470", "WB1031-DUP"],
        "Sursa": ["angieslist", "angieslist", "website"],
        "Charged": [840, 1128.75, 840],
    })
    result = analyze_providers(jobs_df)
    assert "unknown" not in result["Sursa"].values
    assert set(result["Sursa"]) == {"angieslist", "website"}


def test_shifted_row_where_sursa_is_actually_a_job_id_is_flagged():
    jobs_df = pd.DataFrame({
        "Job #": ["AL1", "AL2"],
        "Sursa": ["angieslist", "AL4993"],
        "Charged": [500, 300],
    })
    result = analyze_providers(jobs_df)
    assert "unknown" in result["Sursa"].values


def test_zero_total_revenue_does_not_raise():
    jobs_df = pd.DataFrame({
        "Job #": ["A"],
        "Sursa": ["angieslist"],
        "Charged": [0],
    })
    result = analyze_providers(jobs_df)
    assert result["Revenue_%"].iloc[0] == 0.0
