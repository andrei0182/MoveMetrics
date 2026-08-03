import pandas as pd

from src.processing.build_clean_jobs import build_clean_jobs_from_df


def _sample_df():
    # Job AL4206 are 2 randuri reale: quoted (fara Charged) apoi booked
    # (Charged real). Job AL4557 are 2 plati reale: booked + plata_job_vechi.
    # Amandoua trebuie insumate corect pe Charged, cu un singur rand final.
    return pd.DataFrame({
        "Job #": ["AL4206", "AL4206", "AL4557", "AL4557", "AL9999"],
        "Nume Client": ["A", "A", "B", "B (repeat)", "C"],
        "Sursa": ["angieslist"] * 5,
        "Data": [
            "2026-07-10", "2026-07-13",
            "2026-07-17", "2026-07-22",
            None,
        ],
        "Status": ["quoted", "booked", "won", "plată_job_vechi", "new_lead"],
        "Charged": [0, 630, 1076.25, 341.25, 0],
        "Deposit": [525, 75, 0, 0, 100],
        "Cost": [40.32, 0, 0, 0, 30],
    })


def test_dedup_keeps_one_row_per_job():
    result = build_clean_jobs_from_df(_sample_df())
    assert result["Job #"].nunique() == len(result) == 3


def test_charged_is_summed_across_all_rows_of_a_job():
    result = build_clean_jobs_from_df(_sample_df())
    al4206 = result.loc[result["Job #"] == "AL4206", "Charged"].iloc[0]
    al4557 = result.loc[result["Job #"] == "AL4557", "Charged"].iloc[0]
    assert al4206 == 630
    assert al4557 == 1076.25 + 341.25


def test_last_row_keeps_final_status_not_a_mixed_row():
    # tail(1), nu last(): trebuie sa fie exact ultimul rand real al jobului,
    # nu un amestec de coloane din randuri diferite.
    result = build_clean_jobs_from_df(_sample_df())
    al4557_status = result.loc[result["Job #"] == "AL4557", "Status"].iloc[0]
    assert al4557_status == "plată_job_vechi"


def test_row_with_missing_date_does_not_become_the_final_row():
    # AL9999 are Data=None si e singurul rand al jobului, deci ramane el -
    # dar testam ca na_position="first" nu il muta la finalul altui job.
    df = pd.DataFrame({
        "Job #": ["AL1", "AL1"],
        "Nume Client": ["x", "x"],
        "Sursa": ["angieslist", "angieslist"],
        "Data": [None, "2026-07-05"],
        "Status": ["missing_date_row", "real_last_status"],
        "Charged": [0, 500],
        "Deposit": [0, 0],
        "Cost": [0, 0],
    })
    result = build_clean_jobs_from_df(df)
    assert result["Status"].iloc[0] == "real_last_status"


def test_margin_is_zero_when_no_charge():
    result = build_clean_jobs_from_df(_sample_df())
    al9999 = result.loc[result["Job #"] == "AL9999"].iloc[0]
    assert al9999["Charged"] == 0
    assert al9999["Margin %"] == 0
