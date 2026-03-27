import requests
import json
import os
import argparse
import yaml


def load_secrets(secret_path="secret.yaml"):
    if not os.path.exists(secret_path):
        raise FileNotFoundError(f"Secret file not found: {secret_path}")
    with open(secret_path, "r") as f:
        data = yaml.safe_load(f) or {}
    return data


def load_token(token_filepath: str = "token.secret.txt") -> str:
    if not os.path.exists(token_filepath):
        raise ValueError(f"Token file not found: {token_filepath}")

    with open(token_filepath, "r") as f:
        data = f.readline()

    if not data:
        raise ValueError(f"Token file is empty: {token_filepath}")

    print(f"Token loaded from {token_filepath}")
    return data.strip()


def obtain_access_token(
    secrets: dict, token_url: str = None, save_to: str = None
) -> str:
    print("Obtaining access token...")
    # If a static token is provided, use it
    token = secrets.get("token")
    if token:
        return token

    client_id = secrets.get("client_id")
    client_secret = secrets.get("client_secret")
    if not client_id or not client_secret:
        raise KeyError(
            "secret.yaml must contain either 'token' or both 'client_id' and 'client_secret'"
        )

    if token_url is None:
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

    # Try JSON first, fallback to form-encoded body
    try:
        doc = resp.json()
        access_token = doc.get("access_token") or doc.get("token")
    except ValueError:
        raise
        # parsed = parse_qs(resp.text)
        # access_token = parsed.get("access_token", [None])[0]

    if not access_token:
        raise RuntimeError(f"Could not obtain access token: {resp.text}")

    if save_to:
        with open(save_to, "w") as f:
            f.write(access_token)
        print(f"Access token saved to {save_to}")
    return access_token


def get_metier(code: str, token: str):

    url = (
        f"https://api.francetravail.io/partenaire/rome-metiers/v1/metiers/metier/{code}"
    )
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


def main():

    p = argparse.ArgumentParser(description="Fetch metier by code")
    p.add_argument("code", help="metier code")
    p.add_argument("--secret", "-s", default="secret.yaml", help="path to secret.yaml")
    args = p.parse_args()

    try:
        token = load_token("token.txt")
    except ValueError as err:
        print(f"Token load failed: {err}")

        secret_path = args.secret
        secrets = load_secrets(secret_path)
        token = obtain_access_token(secrets, save_to="token.txt")

    doc_metier = get_metier(args.code, token)

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"metier_{args.code}.yaml")
    with open(output_path, "w") as f:
        yaml.dump(doc_metier, f, allow_unicode=True)
    print(f"Metier data saved to {output_path}")


if __name__ == "__main__":
    main()
