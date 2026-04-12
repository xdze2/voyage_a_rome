"""
Transform ROME YAML fiches → static JSON for the webapp.

Output:
  data/dist/skills.json   — dict of all unique skills
  data/dist/jobs.json     — dict of all jobs with skill refs

Usage (from data_pipeline/):
  python scripts/build_json.py
  python scripts/build_json.py --in-dir ../data/raw --out-dir ../data/dist
"""

import json
from collections import defaultdict
from pathlib import Path

import click
import yaml

SKILL_TYPES = {
    "COMPETENCE-DETAILLEE",
    "MACRO-SAVOIR-FAIRE",
    "MACRO-SAVOIR-ETRE-PROFESSIONNEL",
    "SAVOIR",
}

SECTIONS = {
    "competencesMobiliseesPrincipales": "principal",
    "competencesMobilisees": "standard",
    "competencesMobiliseesEmergentes": "emergent",
}


def load_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def extract_job(doc: dict) -> tuple[dict, dict]:
    """
    Returns (job_entry, skills_seen).
    job_entry = { libelle, principal: [...codes], standard: [...], emergent: [...] }
    skills_seen = list of { code, libelle, type } (deduplicated within the job)
    """
    job = {"libelle": doc.get("libelle", ""), "principal": [], "standard": [], "emergent": []}
    skills_seen = {}

    for section_key, bucket in SECTIONS.items():
        for item in doc.get(section_key) or []:
            code = str(item.get("code", "")).strip()
            libelle = str(item.get("libelle", "")).strip()
            skill_type = item.get("type", "")

            if not code or not libelle:
                continue

            job[bucket].append(code)

            if code not in skills_seen:
                skills_seen[code] = {"libelle": libelle, "type": skill_type}

    return job, skills_seen


@click.command()
@click.option("--in-dir", default="../data/raw", show_default=True, help="Directory with YAML fiches.")
@click.option("--out-dir", default="../data/dist", show_default=True, help="Output directory for JSON files.")
@click.option("--web-dir", default="../webapp/public/data", show_default=True, help="Also copy JSON to webapp public dir.")
def main(in_dir: str, out_dir: str, web_dir: str):
    """Build skills.json and jobs.json from YAML fiches."""
    in_path = Path(in_dir)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    yaml_files = sorted(in_path.glob("metier_*.yaml"))
    if not yaml_files:
        raise click.ClickException(f"No metier_*.yaml files found in {in_path}")

    click.echo(f"Processing {len(yaml_files)} files...")

    jobs: dict[str, dict] = {}
    # skill_code -> { libelle, type, job_count }
    skills_raw: dict[str, dict] = {}
    skill_job_count: dict[str, int] = defaultdict(int)

    for f in yaml_files:
        doc = load_yaml(f)
        code = str(doc.get("code", "")).strip()
        if not code:
            click.echo(f"  skip {f.name} — no code field", err=True)
            continue

        job, skills_seen = extract_job(doc)
        jobs[code] = job

        for code, data in skills_seen.items():
            skill_job_count[code] += 1
            if code not in skills_raw:
                skills_raw[code] = data

    total_jobs = len(jobs)

    # Build final skills dict with freq
    skills: dict[str, dict] = {
        code: {
            "libelle": data["libelle"],
            "type": data["type"],
            "freq": round(skill_job_count[code] / total_jobs, 4),
        }
        for code, data in skills_raw.items()
    }

    # Build reverse index: skill_code -> [job_codes]
    skill_jobs: dict[str, list[str]] = defaultdict(list)
    for job_code, job in jobs.items():
        for bucket in ("principal", "standard", "emergent"):
            for skill_code in job[bucket]:
                skill_jobs[skill_code].append(job_code)

    # Write output
    skills_out = out_path / "skills.json"
    jobs_out = out_path / "jobs.json"
    skill_jobs_out = out_path / "skill_jobs.json"

    with open(skills_out, "w", encoding="utf-8") as f:
        json.dump(skills, f, ensure_ascii=False, separators=(",", ":"))

    with open(jobs_out, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, separators=(",", ":"))

    with open(skill_jobs_out, "w", encoding="utf-8") as f:
        json.dump(dict(skill_jobs), f, ensure_ascii=False, separators=(",", ":"))

    # Stats
    click.echo(f"  {total_jobs} jobs")
    click.echo(f"  {len(skills)} unique skills")

    type_counts = defaultdict(int)
    for s in skills.values():
        type_counts[s["type"]] += 1
    for t, n in sorted(type_counts.items()):
        click.echo(f"    {t}: {n}")

    for p in [skills_out, jobs_out, skill_jobs_out]:
        click.echo(f"  {p.name}: {p.stat().st_size / 1024:.0f} KB")

    if web_dir:
        import shutil
        web_path = Path(web_dir)
        web_path.mkdir(parents=True, exist_ok=True)
        for p in [skills_out, jobs_out, skill_jobs_out]:
            shutil.copy2(p, web_path / p.name)
        click.echo(f"  → copied to {web_path}")

    click.echo("Done.")


if __name__ == "__main__":
    main()
