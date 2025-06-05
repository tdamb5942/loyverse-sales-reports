from src.api import _get_auth_headers
import httpx
import pandas as pd

LOYVERSE_API_BASE_URL = "https://api.loyverse.com/v1.0"


def fetch_all_receipts(start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetches all receipts from the Loyverse API in a date range.

    Handles pagination and returns a pandas DataFrame. Used for reporting.
    """
    url = f"{LOYVERSE_API_BASE_URL}/receipts"
    headers = _get_auth_headers()
    params = {"created_at_min": start_date, "created_at_max": end_date, "limit": 250}

    receipts = []
    while True:
        response = httpx.get(url, headers=headers, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()

        receipts.extend(data.get("receipts", []))
        cursor = data.get("cursor")

        if not cursor:
            break

        params["cursor"] = cursor

    return pd.DataFrame(receipts)


def fetch_all_items() -> pd.DataFrame:
    """
    Fetches all items from the Loyverse API and returns a pandas DataFrame.
    Handles pagination.
    """
    url = f"{LOYVERSE_API_BASE_URL}/items"
    headers = _get_auth_headers()

    items = []
    params = {"limit": 250}
    while True:
        response = httpx.get(url, headers=headers, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        items.extend(data.get("items", []))
        cursor = data.get("cursor")
        if not cursor:
            break
        params["cursor"] = cursor

    return pd.DataFrame(items)


def fetch_all_categories() -> pd.DataFrame:
    """
    Fetches all categories from the Loyverse API and returns a pandas DataFrame.
    """
    url = f"{LOYVERSE_API_BASE_URL}/categories"
    headers = _get_auth_headers()

    response = httpx.get(url, headers=headers, timeout=30.0)
    response.raise_for_status()
    return pd.DataFrame(response.json().get("categories", []))


def get_items_with_categories() -> pd.DataFrame:
    """
    Returns a DataFrame of items with their corresponding category names.
    """
    items_df = fetch_all_items()
    categories_df = fetch_all_categories()
    categories_df = categories_df.rename(
        columns={"id": "category_id", "name": "category_name"}
    )
    return items_df.merge(categories_df, on="category_id", how="left")
