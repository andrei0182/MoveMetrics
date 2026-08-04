import pandas as pd

from src.analysis.provider_analysis import analyze_providers


def test_jobs_count_is_nunique_not_row_count():
    jobs_df = pd.DataFrame({
        "Job #": ["A", "A"],
        "Source": ["Google Ads", "Google Ads"],
        "Charged": [500, 500],
        "Cost": [50, 50],
    })
    result = analyze_providers(jobs_df)
    assert result.loc[result["Source"] == "Google Ads", "Jobs"].iloc[0] == 1


def test_zero_total_revenue_does_not_raise():
    jobs_df = pd.DataFrame({
        "Job #": ["A"], "Source": ["Google Ads"], "Charged": [0], "Cost": [0],
    })
    result = analyze_providers(jobs_df)
    assert result["Revenue_%"].iloc[0] == 0.0
    assert result["Margin_%"].iloc[0] == 0.0


def test_revenue_percent_sums_to_100():
    jobs_df = pd.DataFrame({
        "Job #": ["A", "B"],
        "Source": ["Google Ads", "Website"],
        "Charged": [750, 250],
        "Cost": [50, 20],
    })
    result = analyze_providers(jobs_df)
    assert round(result["Revenue_%"].sum(), 5) == 100.0


def test_cost_and_profit_are_aggregated_per_source():
    jobs_df = pd.DataFrame({
        "Job #": ["A", "B"],
        "Source": ["Google Ads", "Google Ads"],
        "Charged": [500, 300],
        "Cost": [40, 20],
    })
    result = analyze_providers(jobs_df)
    row = result.iloc[0]
    assert row["Cost"] == 60
    assert row["Profit"] == 740
    assert round(row["Margin_%"], 2) == round(740 / 800 * 100, 2)


def test_missing_cost_column_defaults_to_zero():
    jobs_df = pd.DataFrame({"Job #": ["A"], "Source": ["Google Ads"], "Charged": [500]})
    result = analyze_providers(jobs_df)
    assert result["Cost"].iloc[0] == 0
    assert result["Profit"].iloc[0] == 500


def test_sorted_by_profit_descending_most_profitable_first():
    jobs_df = pd.DataFrame({
        "Job #": ["A", "B"],
        "Source": ["Google Ads", "Yelp"],
        "Charged": [500, 100],
        "Cost": [50, 300],
    })
    result = analyze_providers(jobs_df)
    assert result["Source"].iloc[0] == "Google Ads"
    assert result["Source"].iloc[-1] == "Yelp"
    assert result["Profit"].iloc[-1] < 0
