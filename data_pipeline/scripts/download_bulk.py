"""
Download the ROME bulk JSON dataset from data.gouv.fr and extract it.

Source: https://www.data.gouv.fr/datasets/repertoire-operationnel-des-metiers-et-des-emplois-rome/
Stable URL: https://www.data.gouv.fr/api/1/datasets/r/1c893376-8476-4262-9a0e-8df519883e1e

Usage (from data_pipeline/):
  python scripts/download_bulk.py
  python scripts/download_bulk.py --out-dir ../data/RefRomeJson
"""

import zipfile
from io import BytesIO
from pathlib import Path

import click
import requests
from rich.console import Console

console = Console()

BULK_URL = "https://www.data.gouv.fr/api/1/datasets/r/1c893376-8476-4262-9a0e-8df519883e1e"


@click.command()
@click.option(
    "--out-dir",
    default="../data/RefRomeJson",
    show_default=True,
    help="Directory to extract JSON files into.",
)
def main(out_dir: str):
    """Download and extract the ROME bulk JSON dataset."""
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    console.print(f"Downloading ROME bulk dataset from data.gouv.fr...")
    resp = requests.get(BULK_URL, timeout=60, stream=True)
    if not resp.ok:
        raise click.ClickException(f"HTTP {resp.status_code} — {resp.text[:200]}")

    content_type = resp.headers.get("Content-Type", "")
    content_length = int(resp.headers.get("Content-Length", 0))
    console.print(f"  Content-Type: {content_type}")
    if content_length:
        console.print(f"  Size: {content_length / 1024 / 1024:.1f} MB")

    data = resp.content

    if "zip" in content_type or data[:2] == b"PK":
        console.print("  Extracting ZIP...")
        with zipfile.ZipFile(BytesIO(data)) as zf:
            names = zf.namelist()
            console.print(f"  {len(names)} files in archive:")
            for name in names:
                console.print(f"    {name}")
            zf.extractall(out_path)
    else:
        # Direct JSON file
        out_file = out_path / "rome_bulk.json"
        out_file.write_bytes(data)
        console.print(f"  Saved to {out_file}")

    console.print(f"[green]Done.[/green] Files in {out_path}:")
    for p in sorted(out_path.iterdir()):
        console.print(f"  {p.name}  ({p.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
