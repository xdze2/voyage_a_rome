"""Shared HTTP client for the ROME API."""

import requests
from rich.console import Console

from .api_utils import obtain_fresh_token

BASE_URL = "https://api.francetravail.io/partenaire/rome-metiers/v1"
console = Console()


class RateLimitedError(Exception):
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"Rate limited — retry after {retry_after}s")


def get(path: str, token: str, params: dict = None) -> any:
    url = f"{BASE_URL}/{path.lstrip('/')}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    resp = requests.get(url, headers=headers, params=params, timeout=20)

    if resp.status_code == 401:
        console.log("[yellow]Token expired — refreshing...[/yellow]")
        token = obtain_fresh_token()
        headers["Authorization"] = f"Bearer {token}"
        resp = requests.get(url, headers=headers, params=params, timeout=20)

    if resp.status_code == 429:
        retry_after = int(resp.headers.get("Retry-After", 60))
        raise RateLimitedError(retry_after)

    if not resp.ok:
        raise RuntimeError(f"HTTP {resp.status_code} on {url} — {resp.text[:200]}")

    return resp.json()
