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


def test_zero_total_revenue_does_not_raise():
    jobs_df = pd.DataFrame({
        "Job #": ["A"],
        "Sursa": ["angieslist"],
        "Charged": [0],
    })
    result = analyze_providers(jobs_df)
    assert result["Revenue_%"].iloc[0] == 0.0


def test_revenue_percent_sums_to_100():
    jobs_df = pd.DataFrame({
        "Job #": ["A", "B"],
        "Sursa": ["angieslist", "website"],
        "Charged": [750, 250],
    })
    result = analyze_providers(jobs_df)
    assert round(result["Revenue_%"].sum(), 5) == 100.0
