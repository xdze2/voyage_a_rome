"""Pairwise competence comparison UI + ELO ranking for metiers.

Usage:
  python competences_pair_elo.py --competences competences.csv --results results.yaml

Controls:
- press `a` then Enter to pick left competence
- press `b` then Enter to pick right competence
- press `=` then Enter to mark tie
- press space then Enter to skip (no update)
- press `q` then Enter or Ctrl+C to quit (progress saved)

Results are saved incrementally in `results.yaml` which contains:
- matches: list of match records
- elo: mapping competence -> rating
- metier_ranking: computed ranking (metier -> skill_score)
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import random
import sys
import time
from collections import defaultdict
from itertools import combinations
from typing import Dict, List, Tuple

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

DEFAULT_RATING = 1500.0
K_FACTOR = 32.0


def load_competences_csv(path: str) -> Tuple[List[str], Dict[str, List[str]]]:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    comp_list: List[str] = []
    comp_to_metiers: Dict[str, List[str]] = {}
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        hdr = next(r, None)
        for row in r:
            if not row:
                continue
            comp = row[0].strip()
            metiers_col = row[2] if len(row) > 2 else ""
            metiers = [m.strip() for m in metiers_col.split(";") if m.strip()]
            comp_list.append(comp)
            comp_to_metiers[comp] = metiers
    # keep unique and stable order
    seen = set()
    uniq = []
    for c in comp_list:
        if c not in seen:
            seen.add(c)
            uniq.append(c)
    return uniq, comp_to_metiers


def load_results(path: str) -> Dict:
    if not os.path.exists(path):
        return {"matches": [], "elo": {}, "metier_ranking": {}}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {"matches": [], "elo": {}, "metier_ranking": {}}


def save_results(path: str, data: Dict):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True)
    os.replace(tmp, path)


def elo_expectation(ra: float, rb: float) -> float:
    return 1.0 / (1.0 + 10 ** ((rb - ra) / 400.0))


def elo_update(
    ra: float, rb: float, sa: float, k: float = K_FACTOR
) -> Tuple[float, float]:
    ea = elo_expectation(ra, rb)
    eb = 1 - ea
    ra_new = ra + k * (sa - ea)
    rb_new = rb + k * ((1 - sa) - eb)
    return ra_new, rb_new


def compute_metier_scores(
    comp_to_metiers: Dict[str, List[str]], elo: Dict[str, float]
) -> Dict[str, float]:
    metier_scores: Dict[str, float] = defaultdict(float)
    for comp, metiers in comp_to_metiers.items():
        r = float(elo.get(comp, DEFAULT_RATING))
        for m in metiers:
            metier_scores[m] += r
    return dict(metier_scores)


def pair_generator(comps: List[str], existing_pairs: set):
    # generate all unordered pairs
    pairs = list(combinations(comps, 2))
    random.shuffle(pairs)
    for a, b in pairs:
        key = tuple(sorted((a, b)))
        if key in existing_pairs:
            continue
        yield a, b


def show_keys_panel():
    tbl = Table(box=None, show_header=False)
    tbl.add_row("a", "Choose left")
    tbl.add_row("b", "Choose right")
    tbl.add_row("=", "Tie")
    tbl.add_row("space", "Skip (no update)")
    tbl.add_row("q", "Quit and save")
    console.print(Panel(tbl, title="Keys"))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--competences", "-c", default="competences.csv")
    p.add_argument("--results", "-r", default="results.yaml")
    p.add_argument("--k", type=float, default=K_FACTOR, help="ELO K factor")
    args = p.parse_args()

    comps, comp_to_metiers = load_competences_csv(args.competences)
    data = load_results(args.results)
    matches = data.get("matches", [])
    elo = {k: float(v) for k, v in data.get("elo", {}).items()}

    # build existing judged pair set
    judged = set()
    for m in matches:
        a = m.get("a")
        b = m.get("b")
        if a and b:
            judged.add(tuple(sorted((a, b))))

    # ensure all comps have a rating
    for c in comps:
        if c not in elo:
            elo[c] = DEFAULT_RATING

    show_keys_panel()

    try:
        for a, b in pair_generator(comps, judged):
            console.rule()
            ra = elo.get(a, DEFAULT_RATING)
            rb = elo.get(b, DEFAULT_RATING)
            console.print(
                Panel(f"[bold]{a}[/]\n\nRating: {ra:.1f}", title="A"),
                Panel(f"[bold]{b}[/]\n\nRating: {rb:.1f}", title="B"),
            )
            inp = console.input("[cyan]> [/]").strip()

            if inp == "":
                console.print("[yellow]Skipped (empty)[/]")
                judged.add(tuple(sorted((a, b))))
                matches.append(
                    {"a": a, "b": b, "result": "skipped", "ts": int(time.time())}
                )
                data["matches"] = matches
                data["elo"] = elo
                # save skip as judged but do not update elo
                save_results(args.results, data)
                continue

            if inp.lower() == "q":
                console.print("[green]Quitting and saving...[/]")
                break

            if inp == " ":
                console.print("[yellow]Skipped[/]")
                judged.add(tuple(sorted((a, b))))
                matches.append(
                    {"a": a, "b": b, "result": "skipped", "ts": int(time.time())}
                )
                data["matches"] = matches
                data["elo"] = elo
                save_results(args.results, data)
                continue

            if inp == "a":
                sa = 1.0
            elif inp == "b":
                sa = 0.0
            elif inp == "=":
                sa = 0.5
            else:
                console.print(f"[red]Invalid input '{inp}'. Use a, b, =, space, q.[/]")
                continue

            # update elo
            ra_new, rb_new = elo_update(ra, rb, sa, k=args.k)
            elo[a] = ra_new
            elo[b] = rb_new

            judged.add(tuple(sorted((a, b))))
            res = "a" if sa == 1.0 else ("b" if sa == 0.0 else "tie")
            matches.append({"a": a, "b": b, "result": res, "ts": int(time.time())})

            # recompute metier ranking
            metier_scores = compute_metier_scores(comp_to_metiers, elo)
            # save
            data["matches"] = matches
            data["elo"] = elo
            data["metier_ranking"] = metier_scores
            save_results(args.results, data)

            console.print(f"[green]Saved match: {a} vs {b} -> {res}[/]")

    except KeyboardInterrupt:
        console.print("\n[red]Interrupted. Saving results...[/]")

    # final save and summary
    data["matches"] = matches
    data["elo"] = elo
    data["metier_ranking"] = compute_metier_scores(comp_to_metiers, elo)
    save_results(args.results, data)

    # print top metiers
    console.rule("Top Metiers")
    metiers = sorted(data["metier_ranking"].items(), key=lambda x: x[1], reverse=True)
    t = Table("rank", "metier", "score")
    for i, (m, s) in enumerate(metiers[:20], start=1):
        t.add_row(str(i), m, f"{s:.1f}")
    console.print(t)


if __name__ == "__main__":
    main()
