import pandas as pd

from src.analysis.lead_analysis import analyze_leads


def _sample_jobs_df():
    # jobs_df deja deduplicat: 4 leaduri unice, 2 convertite (Charged > 0).
    return pd.DataFrame({
        "Job #": ["A", "B", "C", "D"],
        "Sursa": ["angieslist", "angieslist", "website", "website"],
        "Status": ["booked", "voicemail", "cancelled", "booked"],
        "Charged": [500, 0, 0, 300],
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

    angieslist = by_source[by_source["Sursa"] == "angieslist"].iloc[0]
    assert angieslist["Leads"] == 2
    assert angieslist["Converted"] == 1
    assert angieslist["Conversion_Rate_%"] == 50.0

    website = by_source[by_source["Sursa"] == "website"].iloc[0]
    assert website["Leads"] == 2
    assert website["Converted"] == 1


def test_empty_source_with_no_conversions_does_not_crash():
    jobs_df = pd.DataFrame({
        "Job #": ["A"],
        "Sursa": ["homeadvisor"],
        "Status": ["voicemail"],
        "Charged": [0],
    })
    result = analyze_leads(jobs_df)
    assert result["Converted"] == 0
    assert result["Conversion Rate %"] == 0.0
    assert result["by_source"].iloc[0]["Conversion_Rate_%"] == 0.0


def test_zero_leads_does_not_divide_by_zero():
    jobs_df = pd.DataFrame({"Job #": [], "Sursa": [], "Status": [], "Charged": []})
    result = analyze_leads(jobs_df)
    assert result["Total Leads"] == 0
    assert result["Conversion Rate %"] == 0.0