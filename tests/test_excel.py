import pandas as pd
import pytest

from src.excel.excel_loader import _resolve_sheet_name


def test_sheet_name_trailing_space_is_tolerated(tmp_path):
    # Regresie: sheet-ul real se numeste "CHARGED" (fara spatiu),
    # dar unele module il cautau ca "CHARGED " (cu spatiu).
    file_path = tmp_path / "report.xlsx"
    df = pd.DataFrame({"Job #": ["A"], "Charged": [100]})
    with pd.ExcelWriter(file_path) as writer:
        df.to_excel(writer, sheet_name="CHARGED", index=False)

    assert _resolve_sheet_name(file_path, "CHARGED ") == "CHARGED"
    assert _resolve_sheet_name(file_path, "charged") == "CHARGED"


def test_missing_sheet_raises_clear_error(tmp_path):
    file_path = tmp_path / "report.xlsx"
    df = pd.DataFrame({"Job #": ["A"]})
    with pd.ExcelWriter(file_path) as writer:
        df.to_excel(writer, sheet_name="Other", index=False)

    with pytest.raises(ValueError):
        _resolve_sheet_name(file_path, "CHARGED")
