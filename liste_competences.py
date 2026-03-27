"""
Aggregate competences from YAML files in a directory and write a CSV.

Usage:
  python liste_competences.py --input-dir output --output competences.csv

The script looks for YAML files under the input directory (recursive),
reads each file as a YAML document, extracts competences from the fields:
  - competencesMobilisees
  - competencesMobiliseesEmergentes
  - competencesMobiliseesPrincipales

For each competence it counts occurrences and collects the list of metier
identifiers (file base name or a `code`/`metier` field if present) where it appears.
"""

import argparse
import csv
import os
from collections import defaultdict
from glob import glob

try:
    import yaml
except ImportError:
    raise ImportError("PyYAML is required: pip install pyyaml")


COMPETENCE_FIELDS = [
    "competencesMobilisees",
    "competencesMobiliseesEmergentes",
    "competencesMobiliseesPrincipales",
]


def load_yaml_file(path):
    with open(path, "r", encoding="utf-8") as f:
        try:
            return yaml.safe_load(f) or {}
        except Exception:
            return {}


def extract_metier_identifier(doc, path):
    # Prefer explicit fields if present
    for key in ("code", "metier", "id", "romeCode"):
        val = doc.get(key) if isinstance(doc, dict) else None
        if val:
            return str(val)
    # fallback to filename without extension
    return os.path.splitext(os.path.basename(path))[0]


def normalize_competence(item):
    if item is None:
        return None
    if isinstance(item, str):
        return item.strip()
    # if it's a dict with label/name
    if isinstance(item, dict):
        for k in ("libelle", "label", "intitule", "name"):
            if k in item:
                return str(item[k]).strip()
        # else stringify
        return json_safe_str(item)
    # otherwise stringify
    return str(item).strip()


def json_safe_str(obj):
    try:
        import json

        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        return str(obj)


def aggregate(input_dir):
    pattern = os.path.join(input_dir, "**", "*.yml")
    files = glob(pattern, recursive=True)
    files += glob(os.path.join(input_dir, "**", "*.yaml"), recursive=True)

    counts = defaultdict(int)
    metiers = defaultdict(set)

    for path in files:
        doc = load_yaml_file(path)
        metier_id = extract_metier_identifier(doc, path)

        for field in COMPETENCE_FIELDS:
            vals = None
            if isinstance(doc, dict):
                vals = doc.get(field)
            # if vals is a single string, turn into list
            if vals is None:
                continue
            if isinstance(vals, str):
                vals = [vals]
            if not isinstance(vals, (list, tuple)):
                # could be a dict mapping codes to labels
                if isinstance(vals, dict):
                    vals = list(vals.values())
                else:
                    vals = [vals]

            for v in vals:
                norm = normalize_competence(v)
                if not norm:
                    continue
                counts[norm] += 1
                metiers[norm].add(metier_id)

    # Build list of rows
    rows = []
    for comp, cnt in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        rows.append((comp, cnt, ";".join(sorted(metiers[comp]))))
    return rows


def write_csv(rows, out_path):
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["competence", "frequency", "metiers"])
        for r in rows:
            w.writerow(r)


def main():
    p = argparse.ArgumentParser(description="Aggregate competences from YAML files")
    p.add_argument(
        "--input-dir", "-i", default="output", help="directory containing YAML files"
    )
    p.add_argument("--output", "-o", default="competences.csv", help="output CSV path")
    args = p.parse_args()

    rows = aggregate(args.input_dir)
    write_csv(rows, args.output)
    print(f"Wrote {len(rows)} competences to {args.output}")


if __name__ == "__main__":
    main()
