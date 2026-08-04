import pandas as pd

from src.daily_report.reconciliation import reconcile
from src.daily_report.sample_sources import generate_sample_sources


def test_clean_scenario_has_no_discrepancies():
    leads = pd.DataFrame({
        "Job #": ["A", "B"],
        "Status": ["booked", "quoted"],
    })
    payments = pd.DataFrame({"Job #": ["A"], "Amount": [500]})
    calls = pd.DataFrame({"Job #": ["A", "B"]})

    result = reconcile(leads, payments, calls)

    assert result["missing_payments"] == []
    assert result["orphan_payments"] == []
    assert result["untracked_calls"] == []
    assert result["is_clean"] is True


def test_booked_lead_with_no_payment_is_flagged():
    leads = pd.DataFrame({"Job #": ["A"], "Status": ["booked"]})
    payments = pd.DataFrame({"Job #": [], "Amount": []})
    calls = pd.DataFrame({"Job #": []})

    result = reconcile(leads, payments, calls)

    assert result["missing_payments"] == ["A"]
    assert result["is_clean"] is False


def test_payment_with_no_matching_lead_is_flagged_as_orphan():
    leads = pd.DataFrame({"Job #": ["A"], "Status": ["booked"]})
    payments = pd.DataFrame({"Job #": ["A", "Z"], "Amount": [500, 300]})
    calls = pd.DataFrame({"Job #": []})

    result = reconcile(leads, payments, calls)

    assert result["orphan_payments"] == ["Z"]


def test_call_with_no_matching_lead_is_flagged_as_untracked():
    leads = pd.DataFrame({"Job #": ["A"], "Status": ["quoted"]})
    payments = pd.DataFrame({"Job #": [], "Amount": []})
    calls = pd.DataFrame({"Job #": ["A", "Q"]})

    result = reconcile(leads, payments, calls)

    assert result["untracked_calls"] == ["Q"]


def test_revenue_uses_locale_aware_money_parsing():
    # exercises the same European-decimal-comma parser used elsewhere.
    leads = pd.DataFrame({"Job #": ["A"], "Status": ["booked"]})
    payments = pd.DataFrame({"Job #": ["A"], "Amount": ["1312,5"]})
    calls = pd.DataFrame({"Job #": []})

    result = reconcile(leads, payments, calls)

    assert result["date_summary"]["Revenue"] == 1312.5


def test_summary_counts_are_correct():
    leads = pd.DataFrame({
        "Job #": ["A", "B", "C"],
        "Status": ["booked", "booked", "quoted"],
    })
    payments = pd.DataFrame({"Job #": ["A", "B"], "Amount": [500, 300]})
    calls = pd.DataFrame({"Job #": ["A"]})

    result = reconcile(leads, payments, calls)
    summary = result["date_summary"]

    assert summary["Total Leads"] == 3
    assert summary["Booked"] == 2
    assert summary["Payments Received"] == 2
    assert summary["Revenue"] == 800
    assert summary["Calls Logged"] == 1


def test_empty_inputs_do_not_crash():
    empty = pd.DataFrame({"Job #": []})
    result = reconcile(empty, pd.DataFrame({"Job #": [], "Amount": []}), empty)
    assert result["is_clean"] is True
    assert result["date_summary"]["Total Leads"] == 0


def test_sample_data_generator_produces_known_discrepancies():
    # Regression test: the synthetic generator is designed to always
    # produce exactly these three discrepancy types, so the demo page
    # has something meaningful to show.
    leads, payments, calls = generate_sample_sources(seed=7)
    result = reconcile(leads, payments, calls)

    assert len(result["missing_payments"]) > 0
    assert len(result["orphan_payments"]) > 0
    assert len(result["untracked_calls"]) > 0
    assert result["is_clean"] is False
