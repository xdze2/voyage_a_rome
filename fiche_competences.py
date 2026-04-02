"""
Print and export competences from a single fiche métier YAML file, grouped by type.

Usage:
  python fiche_competences.py output/metier_E1205.yaml
  python fiche_competences.py output/metier_E1205.yaml --output E1205_competences.csv
"""

import argparse
import csv
import sys

try:
    import yaml
except ImportError:
    raise ImportError("PyYAML is required: pip install pyyaml")


COMPETENCE_SECTIONS = [
    "competencesMobiliseesPrincipales",
    "competencesMobilisees",
    "competencesMobiliseesEmergentes",
]

TYPE_ORDER = [
    "COMPETENCE-DETAILLEE",
    "MACRO-SAVOIR-FAIRE",
    "MACRO-SAVOIR-ETRE-PROFESSIONNEL",
    "SAVOIR",
]


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def extract_competences(doc):
    """
    Returns a list of dicts with keys: code, libelle, type, importance.
    A competence may appear in several sections; importance reflects the most
    significant one (principal > standard > emergente).
    """
    PRIORITY = {
        "competencesMobiliseesPrincipales": 1,
        "competencesMobilisees": 2,
        "competencesMobiliseesEmergentes": 3,
    }

    seen = {}  # code -> row dict

    for section in COMPETENCE_SECTIONS:
        items = doc.get(section) or []
        for item in items:
            if not isinstance(item, dict):
                continue
            code = str(item.get("code", ""))
            libelle = item.get("libelle", "")
            comp_type = item.get("type", "")
            riasec_majeur = item.get("riasecMajeur", "")
            riasec_mineur = item.get("riasecMineur", "")

            if (
                code not in seen
                or PRIORITY[section] < PRIORITY[seen[code]["importance"]]
            ):
                seen[code] = {
                    "code": code,
                    "libelle": libelle,
                    "type": comp_type,
                    "importance": section,
                    "riasecMajeur": riasec_majeur,
                    "riasecMineur": riasec_mineur,
                }

    return list(seen.values())


def group_by_type(competences):
    groups = {t: [] for t in TYPE_ORDER}
    other = []
    for c in competences:
        if c["type"] in groups:
            groups[c["type"]].append(c)
        else:
            other.append(c)
    return groups, other


def print_groups(groups, other, metier_code):
    print(f"\n=== Compétences — {metier_code} ===\n")
    for comp_type in TYPE_ORDER:
        items = groups[comp_type]
        if not items:
            continue
        print(f"── {comp_type} ({len(items)}) ──")
        for c in sorted(items, key=lambda x: x["importance"] + x["libelle"]):
            marker = (
                "*"
                if c["importance"] == "competencesMobiliseesPrincipales"
                else (
                    "~" if c["importance"] == "competencesMobiliseesEmergentes" else " "
                )
            )
            print(f"  {marker} [{c['code']}] {c['libelle']}")
        print()
    if other:
        print(f"── OTHER ({len(other)}) ──")
        for c in other:
            print(f"    [{c['code']}] {c['libelle']}  (type={c['type']})")
        print()
    print("Legend: * = principale  ~ = émergente   (space) = standard")


def write_csv(competences, out_path):
    fieldnames = [
        "code",
        "libelle",
        "type",
        "importance",
        "riasecMajeur",
        "riasecMineur",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        # sort by type order then libelle
        type_rank = {t: i for i, t in enumerate(TYPE_ORDER)}
        for row in sorted(
            competences, key=lambda x: (type_rank.get(x["type"], 99), x["libelle"])
        ):
            w.writerow(row)
    print(f"CSV written to {out_path}")


def main():
    p = argparse.ArgumentParser(description="Show competences from a fiche métier YAML")
    p.add_argument("input", help="path to the fiche métier YAML file")
    p.add_argument("--output", "-o", help="output CSV file path (optional)")
    args = p.parse_args()

    doc = load_yaml(args.input)
    metier_code = doc.get("code", args.input)

    competences = extract_competences(doc)
    groups, other = group_by_type(competences)

    print_groups(groups, other, metier_code)

    out_path = args.output or args.input.replace(".yaml", "_competences.csv").replace(
        ".yml", "_competences.csv"
    )
    write_csv(competences, out_path)


if __name__ == "__main__":
    main()
