"""CLI to access ROME API endpoints (list_interest, search_metier).

This is a minimal Click-based starter CLI. Endpoints and params are configurable.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, Optional

import click
import requests
import yaml

from .api_utils import obtain_access_token, obtain_fresh_token

DEFAULT_BASE = "https://api.francetravail.io/partenaire/rome-metiers/v1"


from rich.pretty import pprint
from rich.table import Table
from rich.console import Console


def request_api(
    base: str, path: str, token: str, params: Optional[Dict[str, Any]] = None
) -> Any:
    url = base.rstrip("/") + "/" + path.lstrip("/")
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, params=params, timeout=15)

    if resp.status_code == 401:
        click.echo("Token expired — refreshing...", err=True)
        token = obtain_fresh_token()
        headers["Authorization"] = f"Bearer {token}"
        resp = requests.get(url, headers=headers, params=params, timeout=15)

    if not resp.ok:
        raise click.ClickException(
            f"API error {resp.status_code} on {url}\n  → {resp.text[:200]}"
        )
    try:
        return resp.json()
    except Exception:
        return resp.text


@click.group()
@click.option(
    "--secret",
    "secret_path",
    default="secret.yaml",
    show_default=True,
    help="path to secret.yaml",
)
@click.option(
    "--base-url",
    "base_url",
    default=DEFAULT_BASE,
    show_default=True,
    help="API base URL",
)
@click.pass_context
def cli(ctx: click.Context, secret_path: str, base_url: str):
    """ROME API CLI"""
    ctx.ensure_object(dict)
    ctx.obj["secret_path"] = secret_path
    ctx.obj["base_url"] = base_url


@cli.command("list-interest")
@click.option(
    "--params",
    "params_str",
    default="",
    help="optional query params as key1=val1,key2=val2",
)
@click.pass_context
def list_interest(ctx: click.Context, params_str: str):
    """Call the list_interest endpoint and print JSON result."""
    token = obtain_access_token()
    params = {}
    if params_str:
        for part in params_str.split(","):
            if "=" in part:
                k, v = part.split("=", 1)
                params[k.strip()] = v.strip()
    try:
        # endpoint for interests is /metiers/centre-interet
        out = request_api(
            ctx.obj["base_url"], "metiers/centre-interet", token, params=params
        )
        click.echo(yaml.safe_dump(out, allow_unicode=True))
    except Exception as e:
        raise click.ClickException(str(e))


@cli.command("search")
@click.option("--q", "query", required=True, help="search query")
@click.option("--limit", default=10, help="max results")
@click.pass_context
def search_metier(
    ctx: click.Context,
    query: str,
    limit: int,
) -> None:
    """Call the search endpoint with a query parameter."""
    token = obtain_access_token()
    params = {
        "q": query,  # Les mots recherchés
        "limit": limit,
        "champs": "riasecmineur,riasecmajeur,libelle,code",
    }
    response_data = request_api(
        ctx.obj["base_url"], "metiers/metier/requete", token, params=params
    )
    if response_data is None or (
        isinstance(response_data, dict) and not response_data.get("totalResultats", 0)
    ):
        click.echo("No results found. Exit.")
        return

    total_hits = response_data.get("totalResultats")
    click.echo(f"Nombre de resultats: {total_hits}")

    # Show enumerated results
    hits = response_data.get("resultats", [])
    console = Console()
    table = Table("#", "code", "libelle")
    for i, h in enumerate(hits[:limit], start=1):
        code = (
            h.get("code") or h.get("romeCode") or h.get("id") or h.get("metier") or ""
        )
        lib = h.get("libelle") or h.get("label") or h.get("name") or str(h)
        table.add_row(str(i), str(code), str(lib))
    console.print(table)

    # Ask user to select index to download
    sel = click.prompt(
        "Enter result number to download (0 to cancel)", type=int, default=0
    )
    if sel <= 0 or sel > len(hits[:limit]):
        click.echo("Cancelled")
        return
    chosen = hits[sel - 1]
    code = chosen.get("code")
    if not code:
        raise click.ClickException("Selected item has no code field")

    # fetch full metier detail
    metier = request_api(ctx.obj["base_url"], f"metiers/metier/{code}", token)

    # ensure download dir
    download_dir = "output"
    os.makedirs(download_dir, exist_ok=True)
    out_path = os.path.join(download_dir, f"metier_{code}.yaml")
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(metier, f, allow_unicode=True)
    click.echo(f"Saved metier to {out_path}")


@cli.command("swagger")
@click.option("--out", default="swagger.json", show_default=True, help="output file")
@click.pass_context
def get_swagger(ctx: click.Context, out: str):
    """Fetch the OpenAPI spec and save it locally."""
    token = obtain_access_token()
    data = request_api(ctx.obj["base_url"], "api-docs", token)
    with open(out, "w", encoding="utf-8") as f:
        import json
        json.dump(data, f, ensure_ascii=False, indent=2)
    click.echo(f"Saved OpenAPI spec to {out}")


if __name__ == "__main__":
    cli()
