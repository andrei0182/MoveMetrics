from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


RAW_DATA = BASE_DIR / "data" / "raw"


REPORT_FILE = (
    RAW_DATA / "Report.xlsx"
)