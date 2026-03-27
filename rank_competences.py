"""Interactive terminal app to rank competences using Rich.

Usage:
  python rank_competences.py --input competences.csv --output competences_ranked.yaml

Behavior:
- Loads competences from a CSV (first column is competence text) by default from
  `competences.csv`.
- Loads existing `competences_ranked.yaml` (if present) and resumes without
  losing previously saved ranks.
- For each competence asks the user to choose a level or skip (space).
- Saves after each answer so you can kill and restart safely.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from typing import Dict

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


LEVELS = [
    ("0", "Never"),
    ("1", "Need to learn"),
    ("2", "Willing to learn"),
    ("3", "Beginner"),
    ("4", "Intermediate"),
    ("5", "Expert"),
]

KEYS = {k: label for k, label in LEVELS}

console = Console()


def load_competences_from_csv(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Competences CSV not found: {path}")
    comps = []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        header = next(r, None)
        for row in r:
            if not row:
                continue
            comp = row[0].strip()
            freq = row[1].strip() if len(row) > 1 else ""
            comps.append({"competence": comp, "frequency": freq, "row": row})
    return comps


def load_ranked(path: str) -> Dict[str, Dict]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_ranked(path: str, data: Dict[str, Dict]):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True)
    os.replace(tmp, path)


def show_instructions():
    tbl = Table(show_header=False, box=None)
    for k, label in LEVELS:
        tbl.add_row(f"[{ 'green' if k=='5' else 'cyan' }]{k}[/]", label)
    tbl.add_row("[yellow]space[/]", "Skip this competence")
    tbl.add_row("[red]q[/]", "Quit and save")
    console.print(Panel(tbl, title="Ranking keys"))


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--input", "-i", default="competences.csv", help="CSV with competences"
    )
    p.add_argument(
        "--output", "-o", default="competences_ranked.yaml", help="YAML output file"
    )
    args = p.parse_args()

    try:
        comps = load_competences_from_csv(args.input)
    except Exception as e:
        console.print(f"[red]Error loading input:{e}[/]")
        sys.exit(1)

    ranked = load_ranked(args.output)

    total = len(comps)
    show_instructions()

    try:
        for idx, item in enumerate(comps, start=1):
            comp = item["competence"]
            if comp in ranked:
                continue

            console.rule(f"{idx}/{total}")
            console.print(
                Panel(comp, title="Competence", subtitle=f"freq={item['frequency']}")
            )

            console.print("Choose a level (press key then Enter):", style="bold")
            choice = console.input("[cyan]> [/]").strip()

            if choice == "":
                # treat empty as skip
                console.print("[yellow]Skipped (empty input)[/]")
                continue
            if choice.lower() == "q":
                console.print("[green]Saving and quitting...[/]")
                save_ranked(args.output, ranked)
                return
            if choice == " ":
                console.print("[yellow]Skipped[/]")
                continue
            if choice not in KEYS:
                console.print(
                    f"[red]Invalid choice '{choice}', please use 0-5, space or q[/]"
                )
                # re-ask same competence by decrementing idx logic handled by loop
                # we'll simply continue to next iteration without saving
                # to re-ask, use a small loop instead
                # implement inner loop to re-prompt
                while True:
                    choice = console.input("[cyan]> [/]").strip()
                    if choice in KEYS or choice in (" ", "q", ""):
                        break
                    console.print(f"[red]Invalid choice '{choice}'[/]")

            # handle quit or skip after re-prompt
            if choice.lower() == "q":
                console.print("[green]Saving and quitting...[/]")
                save_ranked(args.output, ranked)
                return
            if choice == " " or choice == "":
                console.print("[yellow]Skipped[/]")
                continue

            label = KEYS.get(choice)
            if not label:
                console.print(f"[red]Unknown key '{choice}'[/]")
                continue

            # record and save immediately
            ranked[comp] = {
                "rank_key": choice,
                "rank_label": label,
                "frequency": item.get("frequency"),
                "timestamp": int(time.time()),
            }
            save_ranked(args.output, ranked)
            console.print(f"[green]Saved: {label}[/]")

    except KeyboardInterrupt:
        console.print("\n[red]Interrupted. Saving progress...[/]")
        save_ranked(args.output, ranked)
        return

    console.print(f"[bold green]Done. Saved {len(ranked)} ranks to {args.output}[/]")


if __name__ == "__main__":
    main()
