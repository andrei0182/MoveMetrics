from unittest.mock import Mock, patch

from src.loaders.google_sheet_loader import load_google_sheet


@patch("src.loaders.google_sheet_loader.requests.get")
def test_load_google_sheet_builds_correct_url_without_gid(mock_get):
    mock_get.return_value = Mock(text="Job #,Charged\nA,100", raise_for_status=lambda: None)
    load_google_sheet("abc123")
    called_url = mock_get.call_args[0][0]
    assert called_url == "https://docs.google.com/spreadsheets/d/abc123/export?format=csv"


@patch("src.loaders.google_sheet_loader.requests.get")
def test_load_google_sheet_builds_correct_url_with_gid(mock_get):
    mock_get.return_value = Mock(text="Job #,Charged\nA,100", raise_for_status=lambda: None)
    load_google_sheet("abc123", gid="42")
    called_url = mock_get.call_args[0][0]
    assert called_url == "https://docs.google.com/spreadsheets/d/abc123/export?format=csv&gid=42"


@patch("src.loaders.google_sheet_loader.requests.get")
def test_load_google_sheet_strips_column_whitespace(mock_get):
    mock_get.return_value = Mock(text="Job # ,Charged\nA,100", raise_for_status=lambda: None)
    df = load_google_sheet("abc123")
    assert "Job #" in df.columns
