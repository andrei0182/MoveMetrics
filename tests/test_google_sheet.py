import pytest
from unittest.mock import Mock, patch

from src.loaders.google_sheet_loader import load_google_sheet


@patch("src.loaders.google_sheet_loader.requests.get")
def test_load_by_sheet_name_uses_gviz_endpoint(mock_get):
    mock_get.return_value = Mock(
        status_code=200,
        text="Job #,Charged\nA,100",
        raise_for_status=lambda: None,
    )
    load_google_sheet("abc123", sheet_name="CHARGED")
    called_url = mock_get.call_args[0][0]
    assert called_url == (
        "https://docs.google.com/spreadsheets/d/abc123/gviz/tq?tqx=out:csv&sheet=CHARGED"
    )


@patch("src.loaders.google_sheet_loader.requests.get")
def test_load_by_gid_builds_export_url(mock_get):
    mock_get.return_value = Mock(
        status_code=200,
        text="Job #,Charged\nA,100",
        raise_for_status=lambda: None,
    )
    load_google_sheet("abc123", gid="42")
    called_url = mock_get.call_args[0][0]
    assert called_url == "https://docs.google.com/spreadsheets/d/abc123/export?format=csv&gid=42"


@patch("src.loaders.google_sheet_loader.requests.get")
def test_no_gid_or_name_exports_first_sheet(mock_get):
    mock_get.return_value = Mock(
        status_code=200,
        text="Job #,Charged\nA,100",
        raise_for_status=lambda: None,
    )
    load_google_sheet("abc123")
    called_url = mock_get.call_args[0][0]
    assert called_url == "https://docs.google.com/spreadsheets/d/abc123/export?format=csv"


@patch("src.loaders.google_sheet_loader.requests.get")
def test_private_sheet_raises_clear_permission_error(mock_get):
    mock_get.return_value = Mock(status_code=401, text="")
    with pytest.raises(PermissionError):
        load_google_sheet("abc123", sheet_name="CHARGED")


@patch("src.loaders.google_sheet_loader.requests.get")
def test_strips_column_whitespace(mock_get):
    mock_get.return_value = Mock(
        status_code=200,
        text="Job # ,Charged\nA,100",
        raise_for_status=lambda: None,
    )
    df = load_google_sheet("abc123", sheet_name="CHARGED")
    assert "Job #" in df.columns
