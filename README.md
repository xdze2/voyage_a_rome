# 🏛️ Voyage à ROME

> Tous les métiers mènent à ROME. Ce POC aide à trouver lequel.

Application web statique de découverte de métiers via classement de compétences par préférence.
Données : base ROME 4.0 (France Travail, opendata). Aucun backend, aucune donnée collectée.

---

![app_screenshot](app_screenshot_001.png)

## Le principe

On vous présente deux compétences. Vous choisissez celle qui vous attire le plus.
Après une vingtaine de choix, vous obtenez un top 10 de métiers qui correspondent à votre profil.

Le classement utilise l'**ELO** (le même que les échecs) en mode active learning : on ne compare que les compétences qui ont du poids sur le classement courant.

---

## État du projet

| Étape | État |
|---|---|
| Récupération données ROME (bulk data.gouv.fr) | ✅ |
| Transformation JSON → JSON statique web | ✅ |
| App web (Svelte, GitHub Pages) — UI/UX | ✅ |
| Algorithme ELO — convergence | ⚠️ non fonctionnel |

---

## Structure

```
data_pipeline/   scripts Python : transformation JSON
data/
  RefRomeJson/   données bulk ROME (gitignored)
  dist/          JSON générés pour le web (gitignored)
webapp/          app Svelte
docs/            build → GitHub Pages
```

---

## Lancer le webapp

```bash
cd webapp
npm install
npm run dev
```

Les données sont déjà dans `webapp/public/data/`. Aucune credential nécessaire.

Build pour GitHub Pages :
```bash
npm run build   # → docs/
```

---

## Regénérer les données

### 1. Télécharger le bulk ROME

```bash
cd data_pipeline
venv/bin/python scripts/download_bulk.py --out-dir ../data/RefRomeJson
```

### 2. Générer les JSON pour le web

```bash
venv/bin/python scripts/build_json.py --in-dir ../data/RefRomeJson --out-dir ../data/dist
# produit macros.json, jobs.json, skill_parent.json, skills.json, skill_jobs.json
# et les copie automatiquement dans webapp/public/data/
```

---

## Données ROME

- Voir le resumé [ROME_data_description.md](./ROME_data_description.md)
- Doc officiel : https://francetravail.io/produits-partages/catalogue/rome-4-0-metiers/documentation
