# CLAUDE.md — Voyage à Rome

Instructions pour Claude Code. Pas pour les humains (mais ils peuvent lire).

---

## Ce que fait ce projet

POC de recommandation de métiers par classement de compétences (ELO).
Données : bulk ROME 4.0 (data.gouv.fr). Cible : app web statique GitHub Pages.

---

## État actuel

- **UI/UX webapp** : fonctionnelle (Svelte, v1 complète)
- **Pipeline données** : fonctionnelle (bulk JSON → JSON statique pour le web)
- **Algorithme ELO** : **NON FONCTIONNEL** — ne converge pas vers des métiers pertinents (bug ou méthode à revoir)
- **Code API France Travail** : mort (plus utilisé, remplacé par les données bulk)

---

## Structure

```
explo_rome/
├── data_pipeline/               # code Python (fetch, transform)
│   ├── explo_rome/              # package partagé
│   │   ├── api_utils.py         # ⚰️ auth OAuth2 France Travail (code mort)
│   │   └── client.py            # ⚰️ client HTTP ROME API (code mort)
│   ├── scripts/
│   │   ├── build_json.py            # ✅ bulk JSON → macros/jobs/skill_parent.json
│   │   ├── download_bulk.py         # ✅ télécharge le ZIP bulk data.gouv.fr
│   │   ├── download_all.py          # ⚰️ télécharge fiches via API (code mort)
│   │   ├── search_metier.py         # ⚰️ recherche via API (code mort)
│   │   ├── list_interest.py         # ⚰️ liste centres d'intérêt via API (code mort)
│   │   ├── fiche_competences.py     # utilitaire : extrait compétences d'un YAML
│   │   ├── liste_competences.py     # utilitaire : agrège compétences de data/raw/
│   │   └── competences_pair_elo.py  # proto ELO console (rich)
│   ├── requirements.txt
│   └── pyproject.toml
├── data/
│   ├── RefRomeJson/             # données bulk data.gouv.fr (gitignored)
│   │   ├── unix_fiche_emploi_metier_v460.json    # 1584 métiers
│   │   └── unix_arborescence_competence_v460.json # hiérarchie compétences
│   ├── raw/                     # fiches YAML téléchargées via API (gitignored, obsolète)
│   └── dist/                    # JSON générés pour le web (gitignored)
│       ├── macros.json          # 507 macro-compétences {code: {libelle, enjeu}}
│       ├── jobs.json            # 1584 métiers {code: {libelle, principal[], standard[], emergent[], contexts[]}}
│       ├── skills.json          # ~14k compétences détaillées {code: {libelle, category, freq}}
│       ├── skill_parent.json    # 17810 liens enfant→parent
│       └── skill_jobs.json      # index inverse compétence→métiers
├── webapp/                      # app Svelte
│   ├── src/
│   │   ├── App.svelte           # root, state machine (loading/comparing/results)
│   │   ├── main.js
│   │   └── lib/
│   │       ├── store.js         # ⚠️ algorithme ELO + gestion données (À DÉBOGUER)
│   │       ├── ComparisonView.svelte  # interface vote (paires de compétences)
│   │       └── ResultsView.svelte     # top 10 métiers
│   └── public/data/             # copie des fichiers dist/ pour Vite
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

## Secrets (code mort, plus nécessaires pour le workflow normal)

- `secret.yaml` : credentials API France Travail — gitignored
- `token.txt` : token OAuth2 — gitignored

---

## Commandes utiles

```bash
# Regénérer les JSON pour le web (depuis données bulk)
cd data_pipeline
venv/bin/python scripts/build_json.py --in-dir ../data/RefRomeJson --out-dir ../data/dist
# copie automatiquement dans webapp/public/data/

# Lancer le webapp en dev
cd webapp && npm run dev

# Build GitHub Pages
cd webapp && npm run build   # → docs/
```

---

## Algorithme ELO — état et problème connu

L'algo est dans `webapp/src/lib/store.js`.

**Principe implémenté :**
- Toutes les compétences démarrent à ELO 1500
- Vote A > B → mise à jour ELO compétitive (K=32)
- "Les deux" → +0.5×K aux deux
- "Ni l'un ni l'autre" → -0.5×K aux deux
- Propagation 30% aux compétences enfants (`CHILD_PROPAGATION = 0.3`)
- Score métier = Σ(elo_macro × poids) avec poids : principal=3, standard=1, emergent=0.5
- Sélection de paires parmi les 100 premiers métiers courants (active learning)

**Problème :** L'algorithme ne converge pas — les résultats ne reflètent pas les préférences exprimées.
Causes possibles : bug dans le calcul de score, propagation mal calibrée, sélection de paires inefficace, ou approche fondamentalement inadaptée.

---

## Données ROME — structure JSON web

**macros.json** : `{code: {libelle, enjeu}}`
**jobs.json** : `{code: {libelle, principal: [codes], standard: [codes], emergent: [codes], contexts: [{code, libelle, category}]}}`
**skill_parent.json** : `{child_code: parent_macro_code}` (17810 entrées)

---

## Conventions

- **CLI Python : toujours utiliser `click`, jamais `argparse`**
- Code Python : scripts autonomes dans `data_pipeline/scripts/`, package réutilisable dans `explo_rome/`
- Pas de tests (POC)
- Le frontend est en Svelte dans `webapp/`, build → `docs/` (GitHub Pages)
- Fichiers générés (`data/raw/`, `data/dist/`, `data/RefRomeJson/`) : gitignorés, ne pas supprimer sans vérifier
