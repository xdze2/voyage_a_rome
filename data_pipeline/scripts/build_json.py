"""
Transform ROME bulk JSON (RefRomeJson/) → static JSON for the webapp.

Source data (download with download_bulk.py):
  data/RefRomeJson/unix_fiche_emploi_metier_v460.json     — 1584 job sheets
  data/RefRomeJson/unix_arborescence_competence_v460.json — skill hierarchy

Output:
  data/dist/skills.json       — all unique skills  { code: { libelle, category, freq } }
  data/dist/jobs.json         — all jobs           { code: { libelle, principal, standard, emergent, contexts } }
  data/dist/skill_jobs.json   — reverse index      { skill_code: [job_codes] }
  data/dist/skill_parent.json — hierarchy          { child_ogr: parent_ogr }

Skill categories (from bulk data nomenclature):
  savoir_faire       → 31 enjeux métier (Animation, Conception, Soin, ...)
  savoir_etre        → "Savoir-être professionnels"
  savoirs            → 5 catégories (Techniques professionnelles, Outils, ...)
  contextes_travail  → 6 catégories (Lieux, Horaires, Statut, ...)

Usage (from data_pipeline/):
  python scripts/build_json.py
  python scripts/build_json.py --in-dir ../data/RefRomeJson --out-dir ../data/dist
"""

import json
from collections import defaultdict
from pathlib import Path

import click
from rich.console import Console

console = Console()

# coeur_metier value → bucket name (importance weight in score)
COEUR_TO_BUCKET = {
    "Principale": "principal",
    "Émergente": "emergent",
    None: "standard",
}


def load_json(path: Path) -> dict | list:
    # Bulk files are latin-1 encoded
    with open(path, encoding="latin-1") as f:
        return json.load(f)


def build_hierarchy(in_path: Path) -> tuple[dict, dict]:
    """
    Parse arborescence_competence.
    Returns:
      macros       — { macro_code: { libelle, enjeu } }
      skill_parent — { child_code: macro_code }
    """
    arbo_files = sorted(in_path.glob("unix_arborescence_competence_*.json"))
    if not arbo_files:
        raise click.ClickException(f"No unix_arborescence_competence_*.json found in {in_path}")

    arbo = load_json(arbo_files[0])
    macros: dict[str, dict] = {}
    skill_parent: dict[str, str] = {}

    for domain in arbo["arborescence_competence"]["domaine_competence"]:
        for enjeu in domain["liste_enjeux"]:
            enjeu_label = enjeu["libelle_enjeu"]
            for obj in enjeu["liste_objectifs"]:
                for macro in obj["liste_macro_competences"]:
                    macro_code = str(macro["code_ogr_macro_competence"])
                    macros[macro_code] = {
                        "libelle": macro["libelle_macro_competence"],
                        "enjeu": enjeu_label,
                    }
                    for comp in macro.get("liste_competences", []):
                        skill_parent[str(comp["code_ogr_competence"])] = macro_code

    return macros, skill_parent


def extract_job(job_data: dict) -> tuple[dict, dict]:
    """
    Parse one job from unix_fiche_emploi_metier.
    Returns (job_entry, skills_seen).
      job_entry   = { libelle, principal: [...codes], standard: [...], emergent: [...], contexts: [...] }
      skills_seen = { code: { libelle, category } }
        category is the bulk data enjeu/category label — used by the algo to compare apples with apples.
    """
    libelle = job_data["rome"]["intitule"]

    job = {
        "libelle": libelle,
        "principal": [],
        "standard": [],
        "emergent": [],
        "contexts": [],
    }
    skills_seen: dict[str, dict] = {}

    # Savoir-faire — enjeu label is the category (e.g. "Conception", "Soin", "Animation"...)
    for enjeu in job_data["competences"]["savoir_faire"]["enjeux"]:
        category = enjeu["libelle"]
        for item in enjeu["items"]:
            code = str(item["code_ogr"])
            bucket = COEUR_TO_BUCKET[item.get("coeur_metier")]
            job[bucket].append(code)
            if code not in skills_seen:
                skills_seen[code] = {"libelle": item["libelle"], "category": category}

    # Savoir-être professionnels — single fixed category
    for enjeu in job_data["competences"]["savoir_etre_professionnel"]["enjeux"]:
        category = enjeu["libelle"]  # "Savoir-être professionnels"
        for item in enjeu["items"]:
            code = str(item["code_ogr"])
            bucket = COEUR_TO_BUCKET[item.get("coeur_metier")]
            job[bucket].append(code)
            if code not in skills_seen:
                skills_seen[code] = {"libelle": item["libelle"], "category": category}

    # Savoirs — uses "categories" key (e.g. "Techniques professionnelles", "Produits, outils et matières"...)
    for cat in job_data["competences"]["savoirs"]["categories"]:
        category = cat["libelle"]
        for item in cat["items"]:
            code = str(item["code_ogr"])
            bucket = COEUR_TO_BUCKET[item.get("coeur_metier")]
            job[bucket].append(code)
            if code not in skills_seen:
                skills_seen[code] = {"libelle": item["libelle"], "category": category}

    # Contextes de travail — stored separately, compared within their own category
    for group in job_data["contextes_travail"]:
        category = group["libelle"]
        for item in group["items"]:
            job["contexts"].append({
                "code": str(item["code_ogr"]),
                "libelle": item["libelle"],
                "category": category,
            })

    return job, skills_seen


@click.command()
@click.option("--in-dir", default="../data/RefRomeJson", show_default=True, help="Directory with ROME bulk JSON files.")
@click.option("--out-dir", default="../data/dist", show_default=True, help="Output directory for generated JSON files.")
@click.option("--web-dir", default="../webapp/public/data", show_default=True, help="Also copy JSON to webapp public dir.")
def main(in_dir: str, out_dir: str, web_dir: str):
    """Build skills.json, jobs.json, skill_jobs.json, skill_parent.json from ROME bulk data."""
    in_path = Path(in_dir)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # --- Load job sheets ---
    job_files = sorted(in_path.glob("unix_fiche_emploi_metier_*.json"))
    if not job_files:
        raise click.ClickException(f"No unix_fiche_emploi_metier_*.json found in {in_path}")

    console.print(f"Loading job sheets from {job_files[0].name}...")
    raw_jobs = load_json(job_files[0])
    console.print(f"  {len(raw_jobs)} jobs found")

    # --- Extract jobs and skills ---
    jobs: dict[str, dict] = {}
    skills_raw: dict[str, dict] = {}
    skill_job_count: dict[str, int] = defaultdict(int)

    for job_data in raw_jobs:
        code = job_data["rome"]["code_rome"]
        job, skills_seen = extract_job(job_data)
        jobs[code] = job

        for skill_code, skill_data in skills_seen.items():
            skill_job_count[skill_code] += 1
            if skill_code not in skills_raw:
                skills_raw[skill_code] = skill_data

    total_jobs = len(jobs)

    # --- Build skills dict with frequency ---
    skills: dict[str, dict] = {
        code: {
            "libelle": data["libelle"],
            "category": data["category"],
            "freq": round(skill_job_count[code] / total_jobs, 4),
        }
        for code, data in skills_raw.items()
    }

    # --- Build reverse index: skill_code → [job_codes] ---
    skill_jobs: dict[str, list[str]] = defaultdict(list)
    for job_code, job in jobs.items():
        for bucket in ("principal", "standard", "emergent"):
            for skill_code in job[bucket]:
                skill_jobs[skill_code].append(job_code)

    # --- Build hierarchy: macros + child→parent ---
    console.print("Building skill hierarchy...")
    macros, skill_parent = build_hierarchy(in_path)
    console.print(f"  {len(macros)} macros, {len(skill_parent)} child→parent links")

    # --- Write output ---
    outputs = {
        "skills.json": skills,
        "jobs.json": jobs,
        "skill_jobs.json": dict(skill_jobs),
        "macros.json": macros,
        "skill_parent.json": skill_parent,
    }

    for filename, data in outputs.items():
        p = out_path / filename
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    # --- Stats ---
    console.print(f"\n[green]Results:[/green]")
    console.print(f"  {total_jobs} jobs")
    console.print(f"  {len(skills)} unique skills")

    cat_counts: dict[str, int] = defaultdict(int)
    for s in skills.values():
        cat_counts[s["category"]] += 1
    for t, n in sorted(cat_counts.items()):
        console.print(f"    {t}: {n}")

    ctx_total = sum(len(j["contexts"]) for j in jobs.values())
    console.print(f"  {ctx_total} context entries across all jobs")

    console.print(f"  {len(macros)} macros, {len(skill_parent)} child→parent links")
    console.print()

    for filename in outputs:
        p = out_path / filename
        console.print(f"  {filename}: {p.stat().st_size / 1024:.0f} KB")

    # --- Copy to webapp ---
    if web_dir:
        import shutil
        web_path = Path(web_dir)
        web_path.mkdir(parents=True, exist_ok=True)
        for filename in outputs:
            shutil.copy2(out_path / filename, web_path / filename)
        console.print(f"\n  → copied to {web_path}")

    console.print("\n[green]Done.[/green]")


if __name__ == "__main__":
    main()
