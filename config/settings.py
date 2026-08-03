from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA = BASE_DIR / "data" / "raw"
PROCESSED_DATA = BASE_DIR / "data" / "processed"

# Fisierul zilnic consolidat. Un singur nume, folosit peste tot -
# inainte existau 3 variante diferite (Report.xlsx / Report_JUL.xlsx / Report_AUG.xlsx)
# in fisiere diferite si niciunul nu importa efectiv acest modul.
REPORT_FILE = RAW_DATA / "Report_JUL.xlsx"

PROCESSED_FILE = PROCESSED_DATA / "processed_jobs.xlsx"

# Numele exact al sheet-ului consolidat din raportul zilnic.
# Verificat direct pe fisierul din Drive: sheet-ul se numeste "CHARGED",
# FARA spatiu la final (unele module aveau "CHARGED " cu spatiu -> cautare esuata).
CHARGED_SHEET = "CHARGED"

# Prefixe valide de Job # in sistem (folosite pentru validarea coloanei Sursa
# si pentru identificarea randurilor cu date decalate pe coloane).
VALID_JOB_PREFIXES = ("AL", "HA", "WB", "MN", "QU", "GH", "CF", "GE", "MY", "AF")
