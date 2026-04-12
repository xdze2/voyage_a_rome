"""
Download all ROME métier fiches to data/raw/.

Steps:
  1. GET /metiers/metier?champs=code,libelle  → list of all ~2000 codes
  2. For each code, GET /metiers/metier/{code} → full fiche → YAML

Usage (from data_pipeline/):
  python scripts/download_all.py
  python scripts/download_all.py --out-dir ../data/raw --delay 0.3
"""

import time
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
)

from explo_rome.api_utils import obtain_access_token
from explo_rome.client import RateLimitedError, get

console = Console()


def fetch_all_codes(token: str) -> list[dict]:
    console.log("Fetching list of all métiers...")
    data = get("metiers/metier", token, params={"champs": "code,libelle"})
    console.log(f"  → {len(data)} métiers found")
    return data


def download_all(out_dir: Path, delay: float, token: str):
    out_dir.mkdir(parents=True, exist_ok=True)

    metiers = fetch_all_codes(token)
    time.sleep(delay)  # respect rate limit before first individual fetch

    already = {p.stem.removeprefix("metier_") for p in out_dir.glob("metier_*.yaml")}
    todo = [m for m in metiers if m["code"] not in already]

    console.log(f"  {len(already)} already downloaded, {len(todo)} remaining")

    if not todo:
        console.print("[green]All métiers already downloaded.[/green]")
        return

    errors = []

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Downloading", total=len(todo))

        for m in todo:
            code = m["code"]
            label = m.get("libelle", "")
            progress.update(task, description=f"{code} {label[:30]:<30}")

            try:
                fiche = get(f"metiers/metier/{code}", token)
                out_path = out_dir / f"metier_{code}.yaml"
                with open(out_path, "w", encoding="utf-8") as f:
                    yaml.safe_dump(fiche, f, allow_unicode=True)
            except RateLimitedError as e:
                progress.stop()
                console.print(
                    f"\n[red]Rate limited after {progress.tasks[task].completed} downloads.[/red]"
                    f"\nRetry-After: [yellow]{e.retry_after}s[/yellow]"
                    f"\nRun the script again when ready — already downloaded files are skipped."
                )
                raise SystemExit(1)
            except Exception as e:
                progress.stop()
                console.print(f"\n[red]Unexpected error on {code}: {e}[/red]")
                raise SystemExit(1)

            progress.advance(task)
            time.sleep(delay)

    console.print(f"\n[green]Done.[/green] {len(todo)} saved.")


@click.command()
@click.option(
    "--out-dir",
    default="../data/raw",
    show_default=True,
    help="Output directory for YAML files.",
)
@click.option(
    "--delay",
    default=1.1,
    show_default=True,
    type=float,
    help="Seconds between requests.",
)
def main(out_dir: str, delay: float):
    """Download all ROME métier fiches to data/raw/."""
    token = obtain_access_token()
    download_all(Path(out_dir), delay, token)


if __name__ == "__main__":
    main()
