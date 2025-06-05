from src.api import (
    _get_access_token,
    _get_auth_headers,
    _generate_auth_url,
    _exchange_auth_code_for_token,
)
from unittest.mock import patch, mock_open, MagicMock
import pytest


@pytest.fixture
def good_token_file(tmp_path):
    path = tmp_path / "token.json"
    path.write_text('{"access_token": "test-token"}')
    return path


@pytest.fixture
def missing_key_token_file(tmp_path):
    path = tmp_path / "token.json"
    path.write_text('{"not_a_token": "oops"}')
    return path


@pytest.fixture
def bad_json_token_file(tmp_path):
    path = tmp_path / "token.json"
    path.write_text("not-a-json")
    return path


# Tests that a valid token.json file returns the expected access token string.
def test_get_access_token_success(good_token_file):
    token = _get_access_token(path=str(good_token_file))
    assert token == "test-token"


# Tests that a token file missing 'access_token' raises a KeyError.
def test_get_access_token_missing_key(missing_key_token_file):
    with pytest.raises(KeyError, match="access_token not found in token file"):
        _get_access_token(path=str(missing_key_token_file))


# Tests that an invalid JSON structure raises a ValueError.
def test_get_access_token_invalid_json(bad_json_token_file):
    with pytest.raises(ValueError, match="Invalid JSON in"):
        _get_access_token(path=str(bad_json_token_file))


# Tests that a missing token file raises a FileNotFoundError.
def test_get_access_token_file_not_found(tmp_path):
    missing_path = tmp_path / "does_not_exist.json"
    with pytest.raises(FileNotFoundError, match="not found"):
        _get_access_token(path=str(missing_path))


# Tests that the auth headers are correctly formatted with the token.
def test_get_auth_headers_returns_expected_dict():
    with patch("src.api._get_access_token", return_value="test-token"):
        headers = _get_auth_headers()
        assert headers["Authorization"] == "Bearer test-token"
        assert headers["Content-Type"] == "application/json"


# Tests that the generated OAuth URL contains the correct query parameters.
def test_generate_auth_url_formats_correctly():
    url = _generate_auth_url("client123", "https://redirect.uri", "RECEIPTS_READ")
    assert url.startswith("https://api.loyverse.com/oauth/authorize")
    assert "client_id=client123" in url
    assert "redirect_uri=https://redirect.uri" in url
    assert "scope=RECEIPTS_READ" in url


# Tests that exchanging a code saves the token data using a mocked file write.
def test_exchange_auth_code_for_token_writes_token(tmp_path):
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "abc", "refresh_token": "def"}
    mock_response.raise_for_status.return_value = None

    with patch("httpx.post", return_value=mock_response):
        with patch("builtins.open", mock_open()) as m:
            _exchange_auth_code_for_token(
                "client", "secret", "code", "https://redirect.uri"
            )
            m.assert_called_once()
