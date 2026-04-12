# 🏛️ Voyage à ROME

> Tous les chemins mènent à Rome. Ce POC aide à trouver lequel.

Application web statique de découverte de métiers via classement de compétences par préférence.
Données : base ROME 4.0 (France Travail, opendata). Aucun backend, aucune donnée collectée.

---

## Le principe

On vous présente deux compétences. Vous choisissez celle qui vous attire le plus.
Après une vingtaine de choix, vous obtenez un top 10 de métiers qui correspondent à votre profil.

Le classement utilise l'**ELO** (le même que les échecs) en mode active learning : on ne compare que les compétences qui ont du poids sur le classement courant.

---

## État du projet

| Étape | État |
|---|---|
| Récupération fiches ROME (API France Travail) | ✅ |
| Transformation YAML → JSON statique | ✅ |
| App web (Svelte, GitHub Pages) | ✅ en cours |

---

## Structure

```
data_pipeline/   scripts Python : fetch API, transformation JSON
data/
  raw/           fiches YAML téléchargées (~2 000 métiers)
  dist/          JSON générés pour le web
webapp/          app Svelte
docs/            build → GitHub Pages
```

---

## Générer les données

### 1. Prérequis

Credentials API France Travail dans `data_pipeline/secret.yaml` :
```yaml
client_id: xxx
client_secret: xxx
```
Créer un compte sur https://francetravail.io pour obtenir les credentials.

### 2. Télécharger les fiches ROME

```bash
cd data_pipeline
pip install -e .
python scripts/download_all.py --out-dir ../data/raw
# ~2 000 métiers, ~35 min à 1 req/s
```

Interruptible et resumable — les fiches déjà téléchargées sont ignorées.

### 3. Générer les JSON pour le web

```bash
python scripts/build_json.py --in-dir ../data/raw --out-dir ../data/dist
# produit skills.json, jobs.json, skill_jobs.json
# et les copie automatiquement dans webapp/public/data/
```

---

## Lancer le webapp

```bash
cd webapp
npm install
npm run dev
```

Build pour GitHub Pages :
```bash
npm run build   # → docs/
```

---

## Données ROME

Types de compétences :

| Type | Exemple |
|---|---|
| `COMPETENCE-DETAILLEE` 🛠️ | "Réaliser un storyboard" |
| `MACRO-SAVOIR-FAIRE` 🧩 | "Animer une équipe" |
| `MACRO-SAVOIR-ETRE-PROFESSIONNEL` 🧠 | "Faire preuve de créativité" |
| `SAVOIR` 📚 | "Photoshop", "Typographie" |

Doc API : https://francetravail.io/produits-partages/catalogue/rome-4-0-metiers/documentation
