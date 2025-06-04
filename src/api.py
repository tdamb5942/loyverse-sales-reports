import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import httpx
import pandas as pd
import json
import webbrowser
from dotenv import load_dotenv
import os

load_dotenv()

LOYVERSE_API_BASE_URL = "https://api.loyverse.com/v1.0"


def _get_access_token(path: str = "secrets/token.json") -> str:
    """
    Reads the access token from a local file with error handling.

    Args:
        path (str): Optional path to token file. Defaults to "secrets/token.json".

    Returns:
        str: Access token value.

    Raises:
        FileNotFoundError: If the token file is missing.
        ValueError: If the file contains invalid JSON.
        KeyError: If the token is not found in the JSON.
    """
    try:
        with open(path, "r") as f:
            data = json.load(f)
            if "access_token" not in data:
                raise KeyError("access_token not found in token file")
            return data["access_token"]
    except FileNotFoundError:
        raise FileNotFoundError(f"{path} not found. Please run authorization first.")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in {path} file")


def _get_auth_headers() -> dict:
    """
    Returns authorization headers using the saved access token.
    """
    access_token = _get_access_token()
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


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


def _generate_auth_url(client_id: str, redirect_uri: str, scope: str) -> str:
    """
    Generates the URL to start the OAuth login flow.

    Used only during initial authorization.
    """
    return (
        "https://api.loyverse.com/oauth/authorize"
        f"?response_type=code&client_id={client_id}"
        f"&redirect_uri={redirect_uri}&scope={scope}"
    )


def _exchange_auth_code_for_token(
    client_id: str, client_secret: str, code: str, redirect_uri: str
) -> None:
    """
    Exchanges an OAuth code for an access token and saves it to token.json.

    Used once during the authorization process.
    """
    url = "https://api.loyverse.com/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    response = httpx.post(url, data=payload)
    response.raise_for_status()
    token_data = response.json()
    with open("secrets/token.json", "w") as f:
        json.dump(token_data, f, indent=2)
    print("Access token saved to secrets/token.json")


def authorize():
    """
    Runs the full OAuth flow: opens browser, listens for code, and stores the token.

    Only used when setting up or reauthorizing.
    """
    client_id = os.getenv("LOYVERSE_CLIENT_ID")
    client_secret = os.getenv("LOYVERSE_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise RuntimeError(
            "Missing LOYVERSE_CLIENT_ID or LOYVERSE_CLIENT_SECRET in environment"
        )

    redirect_uri = os.getenv("LOYVERSE_REDIRECT_URI")
    if not redirect_uri:
        raise RuntimeError("Missing LOYVERSE_REDIRECT_URI in environment")
    scope = "RECEIPTS_READ"

    class OAuthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            query = parse_qs(urlparse(self.path).query)
            code = query.get("code", [None])[0]
            if code:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Authorization complete. You may close this window.")
                threading.Thread(
                    target=_exchange_auth_code_for_token,
                    args=(client_id, client_secret, code, redirect_uri),
                ).start()
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Authorization failed.")

    auth_url = _generate_auth_url(client_id, redirect_uri, scope)
    print("Opening browser to authorize...")
    webbrowser.open(auth_url)

    server_address = ("", 8765)
    httpd = HTTPServer(server_address, OAuthHandler)
    print("Listening for callback on http://localhost:8765...")
    httpd.handle_request()
