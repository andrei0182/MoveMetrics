from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA = BASE_DIR / "data" / "raw"
PROCESSED_DATA = BASE_DIR / "data" / "processed"
REPORTS_DATA = BASE_DIR / "data" / "reports"
DEMO_DATA = BASE_DIR / "data" / "demo"

# Portfolio demo: ships with a bundled synthetic dataset so the app runs
# out of the box, with zero setup, on anyone's machine.
DEMO_FILE = DEMO_DATA / "sample_leads.xlsx"

# For a real deployment, point REPORT_FILE at your own daily-report export.
# The filename is deliberately month-agnostic - update the file in place
# (or via a small "set_report.py"-style script) rather than the filename,
# so nothing in the code has to change when the reporting period changes.
REPORT_FILE = RAW_DATA / "report_current.xlsx"

PROCESSED_FILE = PROCESSED_DATA / "processed_jobs.xlsx"

# Set to True to use REPORT_FILE (your own data) instead of the bundled demo.
USE_OWN_DATA = False

# Name of the consolidated sheet/tab that holds one row per lead event.
LEADS_SHEET_NAME = "LEADS"

# --- Data source: Google Sheets (optional) ---
# If GOOGLE_SHEET_ID is set, the app reads live from Google Sheets (tab
# GOOGLE_SHEET_TAB) instead of a local file. Off by default for the demo -
# the bundled sample file is simpler and needs no external dependency.
# Sheet must be shared as "Anyone with the link - Viewer".
GOOGLE_SHEET_ID = None
GOOGLE_SHEET_TAB = LEADS_SHEET_NAME

# Valid Job ID prefixes for this dataset - used by the data-quality rules
# to detect rows where columns got shifted (e.g. a Job ID ends up in the
# Source column instead of a real channel name).
VALID_ID_PREFIXES = ("GA", "FB", "RF", "WB", "YP", "DM")
