import pandas as pd

from src.analysis.provider_analysis import analyze_providers


def test_jobs_count_is_nunique_not_row_count():
    # Doua randuri, un singur Job # -> Jobs trebuie sa fie 1, nu 2.
    jobs_df = pd.DataFrame({
        "Job #": ["A", "A"],
        "Sursa": ["angieslist", "angieslist"],
        "Charged": [500, 500],
        "Cost": [50, 50],
    })
    result = analyze_providers(jobs_df)
    assert result.loc[result["Sursa"] == "angieslist", "Jobs"].iloc[0] == 1


def test_zero_total_revenue_does_not_raise():
    jobs_df = pd.DataFrame({
        "Job #": ["A"],
        "Sursa": ["angieslist"],
        "Charged": [0],
        "Cost": [0],
    })
    result = analyze_providers(jobs_df)
    assert result["Revenue_%"].iloc[0] == 0.0
    assert result["Margin_%"].iloc[0] == 0.0


def test_revenue_percent_sums_to_100():
    jobs_df = pd.DataFrame({
        "Job #": ["A", "B"],
        "Sursa": ["angieslist", "website"],
        "Charged": [750, 250],
        "Cost": [50, 20],
    })
    result = analyze_providers(jobs_df)
    assert round(result["Revenue_%"].sum(), 5) == 100.0


def test_cost_and_profit_are_aggregated_per_provider():
    jobs_df = pd.DataFrame({
        "Job #": ["A", "B"],
        "Sursa": ["angieslist", "angieslist"],
        "Charged": [500, 300],
        "Cost": [40, 20],
    })
    result = analyze_providers(jobs_df)
    row = result.iloc[0]
    assert row["Cost"] == 60
    assert row["Profit"] == 740
    assert round(row["Margin_%"], 2) == round(740 / 800 * 100, 2)


def test_missing_cost_column_defaults_to_zero():
    jobs_df = pd.DataFrame({
        "Job #": ["A"],
        "Sursa": ["angieslist"],
        "Charged": [500],
    })
    result = analyze_providers(jobs_df)
    assert result["Cost"].iloc[0] == 0
    assert result["Profit"].iloc[0] == 500