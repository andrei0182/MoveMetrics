"""
Generates a synthetic dataset for the portfolio demo - a realistic-looking
(but entirely fake) moving-company lead/job report, saved to
data/demo/sample_leads.xlsx with a sheet named per settings.LEADS_SHEET_NAME.

Run:
    python scripts/generate_demo_data.py

Deliberately includes messy, real-world edge cases so the data-quality and
cleaning stages of the pipeline have something meaningful to demonstrate:
  - repeat payments on the same Job # (deposit + balance, or a later payment
    on an already-booked job)
  - a refund (negative Charged)
  - a couple of "shifted column" rows where Source accidentally contains a
    Job ID instead of a channel name
  - varying cost-per-lead and conversion rates per source, including one
    loss-making source
"""

import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import DEMO_FILE, LEADS_SHEET_NAME, VALID_ID_PREFIXES


random.seed(42)

FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael",
    "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan",
    "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Daniel",
    "Nancy", "Matthew", "Lisa", "Anthony", "Betty", "Mark", "Margaret",
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson",
    "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee",
]

# (source name, prefix, cost_per_lead, conversion_rate, avg_job_value)
SOURCES = [
    ("Google Ads",   "GA", 45,  0.12, 1400),
    ("Facebook Ads", "FB", 30,  0.06, 1100),
    ("Referral",     "RF", 0,   0.35, 1600),
    ("Website",      "WB", 0,   0.18, 1300),
    ("Yelp",         "YP", 60,  0.04, 1200),   # loss-making: high cost, low conversion
    ("Direct Mail",  "DM", 8,   0.09, 900),
]

STATUSES_LOST = [
    "new_lead", "voicemail", "no_answer", "no_budget",
    "cancelled", "quoted", "booked_to_competitor",
]

START_DATE = datetime(2026, 7, 1)
DAYS = 30
LEADS_PER_DAY_RANGE = (18, 32)


def _fake_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def _money(value):
    # occasionally render as a European-style decimal-comma string,
    # to keep exercising the locale-aware money parser in the pipeline.
    if random.random() < 0.15:
        return str(round(value, 2)).replace(".", ",")
    return round(value, 2)


def generate():
    rows = []
    job_counter = 1000
    open_jobs = []  # jobs eligible for a later repeat/second payment

    for day in range(DAYS):
        date = START_DATE + timedelta(days=day)
        n_leads = random.randint(*LEADS_PER_DAY_RANGE)

        for _ in range(n_leads):
            source_name, prefix, cost, conv_rate, avg_value = random.choice(SOURCES)
            job_counter += 1
            job_id = f"{prefix}-{job_counter}"

            converted = random.random() < conv_rate

            if converted:
                total_value = round(avg_value * random.uniform(0.6, 1.6), 2)
                deposit = round(total_value * 0.5, 2)
                status = random.choice(["booked", "won"])
                rows.append({
                    "Job #": job_id,
                    "Customer Name": _fake_name(),
                    "Source": source_name,
                    "Date": date.strftime("%Y-%m-%d"),
                    "Status": status,
                    "Charged": _money(deposit),
                    "Deposit": _money(deposit),
                    "Cost": cost,
                })
                open_jobs.append((job_id, source_name, total_value, deposit))
            else:
                status = random.choice(STATUSES_LOST)
                deposit = 0
                if status == "quoted":
                    deposit = round(avg_value * random.uniform(0.4, 0.6), 2)
                rows.append({
                    "Job #": job_id,
                    "Customer Name": _fake_name(),
                    "Source": source_name,
                    "Date": date.strftime("%Y-%m-%d"),
                    "Status": status,
                    "Charged": 0,
                    "Deposit": _money(deposit) if deposit else 0,
                    "Cost": cost,
                })

        # a handful of second payments (balance due) on older booked jobs
        if open_jobs and random.random() < 0.4:
            job_id, source_name, total_value, deposit = open_jobs.pop(
                random.randrange(len(open_jobs))
            )
            balance = round(total_value - deposit, 2)
            if balance > 5:
                rows.append({
                    "Job #": job_id,
                    "Customer Name": "(repeat payment)",
                    "Source": source_name,
                    "Date": date.strftime("%Y-%m-%d"),
                    "Status": "booked",
                    "Charged": _money(balance),
                    "Deposit": 0,
                    "Cost": 0,
                })

    # a couple of refunds
    for _ in range(3):
        source_name, prefix, cost, _, avg_value = random.choice(SOURCES)
        job_counter += 1
        job_id = f"{prefix}-{job_counter}"
        amount = round(avg_value * 0.5, 2)
        rows.append({
            "Job #": job_id,
            "Customer Name": _fake_name(),
            "Source": source_name,
            "Date": (START_DATE + timedelta(days=random.randint(0, DAYS - 1))).strftime("%Y-%m-%d"),
            "Status": "refund",
            "Charged": -amount,
            "Deposit": 0,
            "Cost": cost,
        })

    # a couple of intentionally "dirty" rows: Source column accidentally
    # contains a Job ID (shifted-column data-entry error), to exercise the
    # data-quality business rule in src/rules/data_quality.py
    for _ in range(2):
        job_counter += 1
        job_id = f"{VALID_ID_PREFIXES[0]}-{job_counter}"
        rows.append({
            "Job #": job_id,
            "Customer Name": _fake_name(),
            "Source": f"{VALID_ID_PREFIXES[0]}-{job_counter + 500}",  # looks like a Job ID, not a real source
            "Date": START_DATE.strftime("%Y-%m-%d"),
            "Status": "booked",
            "Charged": 800,
            "Deposit": 800,
            "Cost": 0,
        })

    random.shuffle(rows)

    return pd.DataFrame(rows)


def main():
    df = generate()

    DEMO_FILE.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(DEMO_FILE, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=LEADS_SHEET_NAME, index=False)

    print(f"Generated {len(df)} synthetic rows -> {DEMO_FILE}")


if __name__ == "__main__":
    main()
