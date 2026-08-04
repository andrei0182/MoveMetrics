"""
Settings - shows the current data-source configuration and how to point
this app at your own data instead of the bundled synthetic demo.

Read-only by design: this is a public demo app, so settings aren't
editable live from the UI (that would let one visitor's changes affect
what every other visitor sees). To use your own data, edit
config/settings.py directly and redeploy.
"""

import streamlit as st

from config import settings as cfg


st.title("Settings")
st.caption("Current configuration, and how to point this app at your own data.")

st.subheader("Active Data Source")

if cfg.GOOGLE_SHEET_ID:
    st.success(f"**Google Sheets** — tab `{cfg.GOOGLE_SHEET_TAB}`")
elif cfg.USE_OWN_DATA:
    st.success(f"**Local file** — `{cfg.REPORT_FILE}`")
else:
    st.info(f"**Bundled synthetic demo data** — `{cfg.DEMO_FILE}`")

st.subheader("Configuration")
st.json({
    "USE_OWN_DATA": cfg.USE_OWN_DATA,
    "LEADS_SHEET_NAME": cfg.LEADS_SHEET_NAME,
    "GOOGLE_SHEET_ID": cfg.GOOGLE_SHEET_ID,
    "GOOGLE_SHEET_TAB": cfg.GOOGLE_SHEET_TAB,
    "VALID_ID_PREFIXES": list(cfg.VALID_ID_PREFIXES),
})

st.divider()

st.subheader("Using Your Own Data")
st.markdown(
    "**Option A — local file:**\n"
    "1. Set `USE_OWN_DATA = True` in `config/settings.py`\n"
    "2. Drop your report at `data/raw/report_current.xlsx`, with a sheet "
    f"named `{cfg.LEADS_SHEET_NAME}` containing at least: `Job #`, `Source`, "
    "`Date`, `Status`, `Charged`, `Cost`, `Deposit`\n\n"
    "**Option B — live Google Sheet:**\n"
    "1. Set `GOOGLE_SHEET_ID` in `config/settings.py` to your sheet's ID\n"
    "2. Share the sheet as *Anyone with the link – Viewer*"
)

st.divider()

st.subheader("About")
st.markdown(
    "**MoveMetrics** is a lead-to-revenue analytics suite built to "
    "demonstrate a clean, testable data pipeline architecture "
    "(loaders → cleaning → business rules → analysis → KPIs → dashboard).\n\n"
    "- Tech stack: Python, pandas, Streamlit, Altair, pytest\n"
    "- 69+ automated tests covering the pipeline end to end\n"
    "- All data on this page is synthetic — no real customer information"
)
