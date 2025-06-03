import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import httpx
import pandas as pd
import json
import webbrowser


LOYVERSE_API_BASE_URL = "https://api.loyverse.com/v1.0"


def get_access_token() -> str:
    """Reads the access token from a local file."""
    with open("token.json", "r") as f:
        data = json.load(f)
        return data["access_token"]


def get_auth_headers() -> dict:
    access_token = get_access_token()
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


def fetch_all_receipts(start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch receipts from Loyverse API within a date range and return as DataFrame."""
    url = f"{LOYVERSE_API_BASE_URL}/receipts"
    headers = get_auth_headers()
    params = {"created_at_min": start_date, "created_at_max": end_date, "limit": 250}

    receipts = []
    while True:
        response = httpx.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        receipts.extend(data.get("receipts", []))
        cursor = data.get("cursor")

        if not cursor:
            break

        params["cursor"] = cursor

    return pd.DataFrame(receipts)


def generate_auth_url(client_id: str, redirect_uri: str, scope: str) -> str:
    return (
        "https://api.loyverse.com/oauth/authorize"
        f"?response_type=code&client_id={client_id}"
        f"&redirect_uri={redirect_uri}&scope={scope}"
    )


def exchange_auth_code_for_token(
    client_id: str, client_secret: str, code: str, redirect_uri: str
) -> None:
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
    with open("token.json", "w") as f:
        json.dump(token_data, f, indent=2)
    print("Access token saved to token.json")


# OAuth flow end-to-end using ngrok HTTPS redirect URI
def authorize(client_id: str, client_secret: str):
    redirect_uri = (
        "https://9ad3-2a02-c7c-ae10-4700-91b2-571f-d9a3-d902.ngrok-free.app/callback"
    )
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
                    target=exchange_auth_code_for_token,
                    args=(client_id, client_secret, code, redirect_uri),
                ).start()
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Authorization failed.")

    auth_url = generate_auth_url(client_id, redirect_uri, scope)
    print("Opening browser to authorize...")
    webbrowser.open(auth_url)

    server_address = ("", 8765)
    httpd = HTTPServer(server_address, OAuthHandler)
    print("Listening for callback on http://localhost:8765...")
    httpd.handle_request()
