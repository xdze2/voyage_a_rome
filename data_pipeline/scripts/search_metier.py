"""Search ROME métiers and optionally download a fiche.

Usage (from data_pipeline/):
  python scripts/search_metier.py --q "graphiste"
  python scripts/search_metier.py --q "infirmier" --limit 20 --out-dir ../data/raw
"""

from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.table import Table

from explo_rome.api_utils import obtain_access_token
from explo_rome.client import get

console = Console()


@click.command()
@click.option("--q", "query", required=True, help="Search query.")
@click.option("--limit", default=10, show_default=True, help="Max results to display.")
@click.option("--out-dir", default="../data/raw", show_default=True, help="Directory to save downloaded fiche.")
def main(query: str, limit: int, out_dir: str):
    """Search ROME métiers and download a selected fiche."""
    token = obtain_access_token()

    data = get("metiers/metier/requete", token, params={
        "q": query,
        "limit": limit,
        "champs": "code,libelle,riasecmajeur,riasecmineur",
    })

    hits = data.get("resultats", [])
    total = data.get("totalResultats", 0)

    if not hits:
        click.echo("No results.")
        return

    click.echo(f"{total} result(s) — showing {len(hits)}\n")
    table = Table("#", "code", "libelle")
    for i, h in enumerate(hits, start=1):
        table.add_row(str(i), h.get("code", ""), h.get("libelle", ""))
    console.print(table)

    sel = click.prompt("\nNumber to download (0 to cancel)", type=int, default=0)
    if sel <= 0 or sel > len(hits):
        click.echo("Cancelled.")
        return

    code = hits[sel - 1].get("code")
    fiche = get(f"metiers/metier/{code}", token)

    out_path = Path(out_dir) / f"metier_{code}.yaml"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(fiche, f, allow_unicode=True)
    click.echo(f"Saved → {out_path}")


if __name__ == "__main__":
    main()
