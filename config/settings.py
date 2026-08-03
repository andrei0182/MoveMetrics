from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA = BASE_DIR / "data" / "raw"
PROCESSED_DATA = BASE_DIR / "data" / "processed"
REPORTS_DATA = BASE_DIR / "data" / "reports"

# Fisierul zilnic consolidat. Un singur nume, neutru la luna -
# indiferent daca sursa se numeste Report_JUL.xlsx, Repot_AUG (3).xlsx etc.,
# scripts/set_report.py il copiaza mereu aici, cu acelasi nume fix.
# Asa nu mai trebuie schimbat nimic in cod cand se schimba luna.
REPORT_FILE = RAW_DATA / "Report.xlsx"

PROCESSED_FILE = PROCESSED_DATA / "processed_jobs.xlsx"

# --- Sursa de date: Google Sheets (optional) ---
# Daca GOOGLE_SHEET_ID e completat, dashboard-ul citeste direct din Google
# Sheets (tab-ul GOOGLE_SHEET_TAB) in loc de fisierul local REPORT_FILE.
# ID-ul e partea din URL: https://docs.google.com/spreadsheets/d/<AICI>/edit
# Sheet-ul trebuie partajat "Anyone with the link - Viewer".
GOOGLE_SHEET_ID = "1smQg1rKIB38cJUGgvvJnqb7E_c-HXaqT--5qzFjQWrk"
GOOGLE_SHEET_TAB = "CHARGED"

# Numele exact al sheet-ului consolidat din raportul zilnic local (.xlsx).
# Verificat direct pe fisierul din Drive: sheet-ul se numeste "CHARGED",
# FARA spatiu la final (unele module aveau "CHARGED " cu spatiu -> cautare esuata).
CHARGED_SHEET = "CHARGED"

# Prefixe valide de Job # in sistem (folosite pentru validarea coloanei Sursa
# si pentru identificarea randurilor cu date decalate pe coloane).
VALID_JOB_PREFIXES = ("AL", "HA", "WB", "MN", "QU", "GH", "CF", "GE", "MY", "AF")
