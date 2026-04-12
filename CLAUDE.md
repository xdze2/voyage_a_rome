# CLAUDE.md — Voyage à Rome

Instructions pour Claude Code. Pas pour les humains (mais ils peuvent lire).

---

## Ce que fait ce projet

POC de recommandation de métiers par classement de compétences (ELO).
Données : API ROME 4.0 France Travail. Cible : app web statique GitHub Pages.

---

## Structure

```
voyage-a-rome/
├── data_pipeline/               # code Python (fetch, transform, prototypage)
│   ├── explo_rome/              # package partagé
│   │   ├── api_utils.py         # auth OAuth2 France Travail
│   │   └── client.py            # client HTTP ROME API (get, RateLimitedError)
│   ├── scripts/                 # un script = une tâche
│   │   ├── download_all.py          # télécharge toutes les fiches → data/raw/
│   │   ├── search_metier.py         # recherche interactive + download d'une fiche
│   │   ├── list_interest.py         # liste les centres d'intérêt
│   │   ├── fiche_competences.py     # extrait compétences d'un YAML → CSV
│   │   ├── liste_competences.py     # agrège compétences de tout data/raw/ → CSV
│   │   └── competences_pair_elo.py  # démo ELO interactive en console (rich)
│   ├── requirements.txt
│   └── pyproject.toml
├── data/
│   ├── raw/                     # fiches YAML téléchargées (gitignored)
│   └── dist/                    # JSON générés pour le web (gitignored)
├── webapp/                      # app Svelte (à construire)
├── docs/                        # build Svelte → GitHub Pages
├── claude_logs/                 # notes de session (gitignored)
├── CLAUDE.md
└── README.md
```

---

## Environnement

```bash
data_pipeline/venv/bin/python   # toujours utiliser le venv du projet
```

Dépendances : `pyyaml`, `requests`, `rich`. Voir `data_pipeline/requirements.txt`.

---

## Secrets

- `secret.yaml` : credentials API France Travail (`client_id`, `client_secret`) — gitignored
- `token.txt` : token OAuth2 mis en cache — gitignored

Ne jamais commiter ces fichiers.

---

## Commandes utiles

```bash
cd data_pipeline

# Télécharger toutes les fiches (~2000 métiers, ~35 min à 1.1s/req)
venv/bin/python scripts/download_all.py --out-dir ../data/raw

# Rechercher et télécharger une fiche (interactif)
venv/bin/python scripts/search_metier.py --q "graphiste"

# Lister les centres d'intérêt
venv/bin/python scripts/list_interest.py

# Extraire les compétences d'une fiche
venv/bin/python scripts/fiche_competences.py ../data/raw/metier_E1205.yaml

# Agréger toutes les compétences
venv/bin/python scripts/liste_competences.py --input-dir ../data/raw --output ../data/dist/competences.csv

# Lancer la démo ELO console
venv/bin/python scripts/competences_pair_elo.py
```

---

## Données ROME — structure YAML

Champs pertinents d'une fiche métier :

```yaml
code: E1205
competencesMobiliseesPrincipales: [...]   # cœur du métier
competencesMobilisees: [...]              # compétences secondaires
competencesMobiliseesEmergentes: [...]    # émergentes
```

Chaque compétence a : `code`, `libelle`, `type`, optionnellement `riasecMajeur/Mineur`.

Types : `COMPETENCE-DETAILLEE`, `MACRO-SAVOIR-FAIRE`, `MACRO-SAVOIR-ETRE-PROFESSIONNEL`, `SAVOIR`.

---

## Conventions

- **CLI Python : toujours utiliser `click`, jamais `argparse`**
- Code Python : scripts autonomes dans `data_pipeline/scripts/`, package réutilisable dans `explo_rome/`
- Pas de tests pour l'instant (c'est un POC)
- Le frontend est en Svelte dans `webapp/`, build → `docs/` (GitHub Pages)
- Fichiers générés (`data/raw/`, `data/dist/`) : gitignorés, ne pas supprimer sans vérifier

---

## Ce qui n'existe pas encore

- Le frontend web (toute la partie `web/`)
- La conversion YAML → JSON statique pour le navigateur
- Le déploiement GitHub Pages
