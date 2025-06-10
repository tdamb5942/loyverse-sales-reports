from src.data_fetching import fetch_all_receipts, fetch_all_items, fetch_all_categories
from unittest.mock import patch, MagicMock
import pandas as pd


# Tests that the receipts API call returns a DataFrame and parses results correctly.
def test_fetch_all_receipts_returns_dataframe():
    mock_data = {
        "receipts": [
            {"receipt_number": "123", "total_money": 100},
            {"receipt_number": "124", "total_money": 200},
        ],
        "cursor": None,
    }

    with patch(
        "src.data_fetching._get_auth_headers",
        return_value={"Authorization": "Bearer test"},
    ):
        with patch(
            "httpx.get",
            return_value=MagicMock(
                json=lambda: mock_data, raise_for_status=lambda: None
            ),
        ):
            df = fetch_all_receipts("2025-01-01T00:00:00Z", "2025-01-02T00:00:00Z")
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 2
            assert set(df.columns) >= {"receipt_number", "total_money"}


def test_fetch_all_items_returns_dataframe():
    mock_data = {
        "items": [
            {"id": "item1", "item_name": "Smoothie", "category_id": "cat1"},
            {"id": "item2", "item_name": "Bracelet", "category_id": "cat2"},
        ],
        "cursor": None,
    }

    with patch(
        "src.data_fetching._get_auth_headers",
        return_value={"Authorization": "Bearer test"},
    ):
        with patch(
            "httpx.get",
            return_value=MagicMock(
                json=lambda: mock_data, raise_for_status=lambda: None
            ),
        ):
            df = fetch_all_items()
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 2
            assert set(df.columns) >= {"id", "item_name", "category_id"}


def test_fetch_all_categories_returns_dataframe():
    mock_data = {
        "categories": [
            {"id": "cat1", "name": "Drinks"},
            {"id": "cat2", "name": "Jewellery"},
        ]
    }

    with patch(
        "src.data_fetching._get_auth_headers",
        return_value={"Authorization": "Bearer test"},
    ):
        with patch(
            "httpx.get",
            return_value=MagicMock(
                json=lambda: mock_data, raise_for_status=lambda: None
            ),
        ):
            df = fetch_all_categories()
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 2
            assert set(df.columns) >= {"id", "name"}
