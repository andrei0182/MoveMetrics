import pandas as pd

from src.analysis.trend_analysis import analyze_trends


def test_new_leads_attributed_to_first_appearance():
    df = pd.DataFrame({
        "Job #": ["A", "A", "B"],
        "Date": ["2026-08-01", "2026-08-03", "2026-08-01"],
        "Charged": [0, 500, 0],
    })
    result = analyze_trends(df)
    day1 = result[result["Date"] == pd.Timestamp("2026-08-01").date()].iloc[0]
    assert day1["New Leads"] == 2  # A and B both first seen on day 1


def test_conversion_attributed_to_the_day_it_actually_converts():
    # A is first seen day 1 but converts on day 3 - conversion must
    # land on day 3, not day 1.
    df = pd.DataFrame({
        "Job #": ["A", "A"],
        "Date": ["2026-08-01", "2026-08-03"],
        "Charged": [0, 500],
    })
    result = analyze_trends(df)

    day1 = result[result["Date"] == pd.Timestamp("2026-08-01").date()].iloc[0]
    day3 = result[result["Date"] == pd.Timestamp("2026-08-03").date()].iloc[0]

    assert day1["Conversions"] == 0
    assert day3["Conversions"] == 1
    assert day3["Revenue"] == 500


def test_revenue_summed_per_day_across_multiple_jobs():
    df = pd.DataFrame({
        "Job #": ["A", "B"],
        "Date": ["2026-08-01", "2026-08-01"],
        "Charged": [300, 200],
    })
    result = analyze_trends(df)
    assert result.iloc[0]["Revenue"] == 500


def test_missing_date_column_returns_empty_frame_with_expected_columns():
    df = pd.DataFrame({"Job #": ["A"], "Charged": [100]})
    result = analyze_trends(df)
    assert list(result.columns) == ["Date", "Revenue", "New Leads", "Conversions"]
    assert len(result) == 0


def test_rows_with_invalid_dates_are_dropped_not_crashed():
    df = pd.DataFrame({
        "Job #": ["A", "B"],
        "Date": ["2026-08-01", "not a date"],
        "Charged": [100, 200],
    })
    result = analyze_trends(df)
    assert len(result) == 1


def test_european_decimal_comma_is_parsed_in_revenue():
    df = pd.DataFrame({
        "Job #": ["A"], "Date": ["2026-08-01"], "Charged": ["1312,5"],
    })
    result = analyze_trends(df)
    assert result.iloc[0]["Revenue"] == 1312.5


def test_results_are_sorted_chronologically():
    df = pd.DataFrame({
        "Job #": ["A", "B", "C"],
        "Date": ["2026-08-03", "2026-08-01", "2026-08-02"],
        "Charged": [0, 0, 0],
    })
    result = analyze_trends(df)
    assert list(result["Date"]) == sorted(result["Date"])
