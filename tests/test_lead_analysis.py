import pandas as pd

from src.analysis.lead_analysis import analyze_leads


def _sample_jobs_df():
    return pd.DataFrame({
        "Job #": ["A", "B", "C", "D"],
        "Source": ["Google Ads", "Google Ads", "Website", "Website"],
        "Status": ["booked", "voicemail", "cancelled", "booked"],
        "Charged": [500, 0, 0, 300],
        "Cost": [40, 40, 20, 20],
    })


def test_total_leads_counts_unique_jobs_regardless_of_status():
    result = analyze_leads(_sample_jobs_df())
    assert result["Total Leads"] == 4


def test_converted_counts_only_positive_charged():
    result = analyze_leads(_sample_jobs_df())
    assert result["Converted"] == 2


def test_conversion_rate_is_percentage():
    result = analyze_leads(_sample_jobs_df())
    assert result["Conversion Rate %"] == 50.0


def test_by_source_breaks_down_leads_and_conversions():
    result = analyze_leads(_sample_jobs_df())
    by_source = result["by_source"]

    ga = by_source[by_source["Source"] == "Google Ads"].iloc[0]
    assert ga["Leads"] == 2
    assert ga["Converted"] == 1
    assert ga["Conversion_Rate_%"] == 50.0

    website = by_source[by_source["Source"] == "Website"].iloc[0]
    assert website["Leads"] == 2
    assert website["Converted"] == 1


def test_cost_per_conversion_is_cost_divided_by_converted():
    result = analyze_leads(_sample_jobs_df())
    by_source = result["by_source"]
    ga = by_source[by_source["Source"] == "Google Ads"].iloc[0]
    assert ga["Cost"] == 80
    assert ga["Cost_Per_Conversion"] == 80.0


def test_cost_per_conversion_is_none_when_no_conversions():
    jobs_df = pd.DataFrame({
        "Job #": ["A", "B"],
        "Source": ["Yelp", "Yelp"],
        "Status": ["voicemail", "no_answer"],
        "Charged": [0, 0],
        "Cost": [30, 30],
    })
    result = analyze_leads(jobs_df)
    row = result["by_source"][result["by_source"]["Source"] == "Yelp"].iloc[0]
    assert row["Converted"] == 0
    assert pd.isna(row["Cost_Per_Conversion"])


def test_missing_cost_column_defaults_to_zero():
    jobs_df = pd.DataFrame({
        "Job #": ["A"], "Source": ["Google Ads"], "Status": ["booked"], "Charged": [500],
    })
    result = analyze_leads(jobs_df)
    assert result["by_source"]["Cost"].iloc[0] == 0


def test_empty_source_with_no_conversions_does_not_crash():
    jobs_df = pd.DataFrame({
        "Job #": ["A"], "Source": ["Yelp"], "Status": ["voicemail"],
        "Charged": [0], "Cost": [10],
    })
    result = analyze_leads(jobs_df)
    assert result["Converted"] == 0
    assert result["Conversion Rate %"] == 0.0
    assert result["by_source"].iloc[0]["Conversion_Rate_%"] == 0.0


def test_zero_leads_does_not_divide_by_zero():
    jobs_df = pd.DataFrame({
        "Job #": [], "Source": [], "Status": [], "Charged": [], "Cost": []
    })
    result = analyze_leads(jobs_df)
    assert result["Total Leads"] == 0
    assert result["Conversion Rate %"] == 0.0
