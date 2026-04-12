# CLAUDE.md — Voyage à Rome

Instructions pour Claude Code. Pas pour les humains (mais ils peuvent lire).

---

## Ce que fait ce projet

POC de recommandation de métiers par classement de compétences (ELO).
Données : API ROME 4.0 France Travail. Cible : app web statique GitHub Pages.

---

## Structure

```
explo_rome/
├── explo_rome/                  # package Python
│   ├── api_utils.py             # auth OAuth2 France Travail
│   └── rome_api_cli.py          # CLI fetch fiches métier → output/
├── fiche_competences.py         # extrait compétences d'un YAML → CSV
├── liste_competences.py         # agrège compétences de tout output/ → CSV
├── competences_pair_elo.py      # démo ELO interactive en console (rich)
├── output/                      # fiches YAML téléchargées (14 métiers sample)
├── competences.csv              # agrégation compétences (généré)
└── results.yaml                 # résultats ELO (généré, ne pas commiter)
```

---

## Environnement

```bash
venv/bin/python   # toujours utiliser le venv du projet
```

Dépendances : `pyyaml`, `requests`, `rich`. Voir `requirements.txt`.

---

## Secrets

- `secret.yaml` : credentials API France Travail (`client_id`, `client_secret`) — gitignored
- `token.txt` : token OAuth2 mis en cache — gitignored

Ne jamais commiter ces fichiers.

---

## Commandes utiles

```bash
# Télécharger une fiche métier
venv/bin/python -m explo_rome.rome_api_cli search --q "graphiste"

# Extraire les compétences d'une fiche
venv/bin/python fiche_competences.py output/metier_E1205.yaml

# Agréger toutes les compétences
venv/bin/python liste_competences.py --input-dir output --output competences.csv

# Lancer la démo ELO console
venv/bin/python competences_pair_elo.py
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

- Code Python : scripts autonomes à la racine, package réutilisable dans `explo_rome/`
- Pas de tests pour l'instant (c'est un POC)
- Le frontend cible sera du HTML/JS statique dans un dossier `web/` ou `docs/` (à décider)
- Fichiers générés (`*.csv`, `results.yaml`, `output/`) : ne pas supprimer sans vérifier

---

## Ce qui n'existe pas encore

- Le frontend web (toute la partie `web/`)
- La conversion YAML → JSON statique pour le navigateur
- Le déploiement GitHub Pages
