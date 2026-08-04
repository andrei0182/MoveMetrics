"""
Splits a report DataFrame into one Excel sheet per day, plus a TOTAL
sheet with everything combined - a common "monthly workbook" convention
for operations teams that review activity day by day, but also want a
single consolidated view for the whole period.

Pure function, no Streamlit, no file I/O by default (returns bytes in
memory) - fully testable in isolation.
"""

from io import BytesIO

import pandas as pd


def _sheet_name_for_day(day):
    if day is None or pd.isna(day):
        return "Unknown Date"
    # Excel sheet names: max 31 chars, no : \ / ? * [ ]
    return day.strftime("%d.%b").upper()


def generate_monthly_workbook(df, date_column="Date"):
    """
    Returns the bytes of an in-memory .xlsx workbook: one sheet per
    calendar day found in `date_column` (named e.g. "01.AUG"), plus a
    final "TOTAL" sheet containing every row, in the original order.
    """

    data = df.copy()

    if date_column in data.columns:
        data[date_column] = pd.to_datetime(data[date_column], errors="coerce")

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        if date_column in data.columns:
            day_series = data[date_column].dt.date
            seen_names = set()

            for day in sorted(day_series.dropna().unique()):
                day_df = data[day_series == day]
                sheet_name = _sheet_name_for_day(pd.Timestamp(day))[:31]

                # guard against an unlikely name collision
                base_name, suffix = sheet_name, 1
                while sheet_name in seen_names:
                    suffix += 1
                    sheet_name = f"{base_name[:28]}_{suffix}"
                seen_names.add(sheet_name)

                day_df.to_excel(writer, sheet_name=sheet_name, index=False)

            unknown_df = data[day_series.isna()]
            if len(unknown_df) > 0:
                unknown_df.to_excel(writer, sheet_name="Unknown Date", index=False)

        data.to_excel(writer, sheet_name="TOTAL", index=False)

    return output.getvalue()
