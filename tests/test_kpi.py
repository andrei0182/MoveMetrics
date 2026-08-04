import pandas as pd

from src.models.kpi import calculate_kpis


def test_average_job_value_is_per_job_not_per_row():
    jobs_df = pd.DataFrame({
        "Job #": ["A", "B", "C"],
        "Charged": [1000, 500, 0],
        "Deposit": [0, 0, 300],
    })
    kpis = calculate_kpis(jobs_df)
    assert kpis["Total Jobs"] == 3
    assert kpis["Total Charged"] == 1500
    assert kpis["Average Job Value"] == 500


def test_refunds_counted_from_negative_charged():
    jobs_df = pd.DataFrame({
        "Job #": ["A", "B"],
        "Charged": [840, -840],
        "Deposit": [0, 0],
    })
    kpis = calculate_kpis(jobs_df)
    assert kpis["Refunds"] == 1


def test_empty_df_does_not_crash():
    jobs_df = pd.DataFrame({"Job #": [], "Charged": [], "Deposit": []})
    kpis = calculate_kpis(jobs_df)
    assert kpis["Total Jobs"] == 0
    assert kpis["Average Job Value"] == 0.0
