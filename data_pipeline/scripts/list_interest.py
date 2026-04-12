"""List all ROME centres d'intérêt and print as YAML.

Usage (from data_pipeline/):
  python scripts/list_interest.py
  python scripts/list_interest.py --out ../data/dist/interests.yaml
"""

import click
import yaml

from explo_rome.api_utils import obtain_access_token
from explo_rome.client import get


@click.command()
@click.option("--out", default=None, help="Save output to file instead of stdout.")
def main(out):
    """List all ROME centres d'intérêt."""
    token = obtain_access_token()
    data = get("metiers/centre-interet", token)
    output = yaml.safe_dump(data, allow_unicode=True)

    if out:
        with open(out, "w", encoding="utf-8") as f:
            f.write(output)
        click.echo(f"Saved to {out}")
    else:
        click.echo(output)


if __name__ == "__main__":
    main()
