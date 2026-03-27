import requests
import os
import yaml

from typing import Tuple

TOKEN_FILEPATH = "token.secret.txt"
SECRET_FILEPATH = "secret.yaml"


def _load_secrets_file(secret_filepath: str) -> Tuple[str, str]:
    """Load client_id and client_secret from a YAML file."""
    if not os.path.exists(secret_filepath):
        raise FileNotFoundError(f"Secret file not found ({secret_filepath}).")

    with open(secret_filepath, "r") as f:
        secrets = yaml.safe_load(f) or {}

    client_id = secrets.get("client_id")
    client_secret = secrets.get("client_secret")
    if not client_id or not client_secret:
        raise KeyError(
            f"{secret_filepath} yaml file must contain both 'client_id' and 'client_secret' keys."
        )

    return client_id, client_secret


def _load_token_file(token_filepath: str) -> str:
    """Load a static token from a file."""
    if not os.path.exists(token_filepath):
        raise ValueError(f"Token file not found ({token_filepath}).")

    with open(token_filepath, "r") as f:
        data = f.readline()

    if not data:
        raise ValueError(f"Token file is empty ({token_filepath}).")

    return data.strip()


def _request_access_token(
    client_id: str, client_secret: str, save_to: str = None
) -> str:
    """Obtain an access token using the client credentials flow."""
    print("Requesting access token...")

    token_url = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire"

    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "nomenclatureRome api_rome-metiersv1",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(token_url, data=data, headers=headers, timeout=10)
    resp.raise_for_status()

    doc = resp.json()
    access_token = doc.get("access_token") or doc.get("token")

    if not access_token:
        raise RuntimeError(f"Could not obtain access token: {resp.text}")

    if save_to is not None:
        with open(save_to, "w") as f:
            f.write(access_token)
        print(f"Access token saved to {save_to}")
    return access_token


def obtain_access_token() -> str:

    try:
        token = _load_token_file(TOKEN_FILEPATH)
        return token
    except ValueError as err:
        print(
            f"Token load failed ({err}). Attempting to obtain a new token using client credentials..."
        )

    try:
        secrets = _load_secrets_file(SECRET_FILEPATH)
    except FileNotFoundError as err:
        raise RuntimeError(
            f"Failed to load secrets from {SECRET_FILEPATH}: {err}. Abort."
        ) from err

    token = _request_access_token(*secrets, save_to=TOKEN_FILEPATH)

    return token
