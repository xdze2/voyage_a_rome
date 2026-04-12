import os
import yaml
import requests
from typing import Tuple

TOKEN_FILEPATH = "token.secret.txt"
SECRET_FILEPATH = "secret.yaml"


def _load_secrets_file(secret_filepath: str) -> Tuple[str, str]:
    if not os.path.exists(secret_filepath):
        raise FileNotFoundError(f"Secret file not found: {secret_filepath}")
    with open(secret_filepath, "r") as f:
        secrets = yaml.safe_load(f) or {}
    client_id = secrets.get("client_id")
    client_secret = secrets.get("client_secret")
    if not client_id or not client_secret:
        raise KeyError(f"{secret_filepath} must contain 'client_id' and 'client_secret'.")
    return client_id, client_secret


def _load_token_file(token_filepath: str) -> str:
    if not os.path.exists(token_filepath):
        raise FileNotFoundError(f"Token file not found: {token_filepath}")
    with open(token_filepath, "r") as f:
        data = f.readline().strip()
    if not data:
        raise ValueError(f"Token file is empty: {token_filepath}")
    return data


def _request_fresh_token() -> str:
    """Obtain a fresh token from the OAuth2 endpoint and cache it."""
    client_id, client_secret = _load_secrets_file(SECRET_FILEPATH)
    print("Requesting new access token...")
    resp = requests.post(
        "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire",
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "nomenclatureRome api_rome-metiersv1",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    resp.raise_for_status()
    token = resp.json().get("access_token") or resp.json().get("token")
    if not token:
        raise RuntimeError(f"No token in response: {resp.text}")
    with open(TOKEN_FILEPATH, "w") as f:
        f.write(token)
    print(f"Token saved to {TOKEN_FILEPATH}")
    return token


def obtain_access_token() -> str:
    """Load cached token, or fetch a new one if missing."""
    try:
        return _load_token_file(TOKEN_FILEPATH)
    except (FileNotFoundError, ValueError):
        return _request_fresh_token()


def obtain_fresh_token() -> str:
    """Force-refresh the token (call this after a 401)."""
    if os.path.exists(TOKEN_FILEPATH):
        os.remove(TOKEN_FILEPATH)
    return _request_fresh_token()
