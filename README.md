# Voyage à Rome

> Tous les chemins mènent à Rome. Ce POC aide à trouver lequel.

Application web statique de découverte de métiers via classement de compétences par préférence.
Données : base ROME 4.0 (France Travail, opendata). Aucun backend.

---

## Le principe

On vous présente deux compétences. Vous choisissez celle qui vous attire le plus.
Après une vingtaine de choix, vous obtenez un top 10 de métiers qui correspondent à votre profil.

Le classement utilise l'**ELO** (le même que les échecs). Les métiers sont scorés par la somme ELO de leurs compétences requises.

---

## État du projet

| Étape | Outil | État |
|---|---|---|
| Récupération fiches ROME (API) | `explo_rome/rome_api_cli.py` | ✅ |
| Extraction compétences d'une fiche | `fiche_competences.py` | ✅ |
| Agrégation toutes compétences | `liste_competences.py` | ✅ |
| Démo ELO en console | `competences_pair_elo.py` | ✅ |
| App web statique | — | 🔲 |

---

## Données ROME

- ~2 000 métiers, ~30 000 compétences, ~30 compétences/métier
- `output/` : échantillon de 14 fiches YAML (exploration)
- `competences.csv` : agrégation des compétences (621 entrées sur l'échantillon)

Types de compétences :

| Type | Exemple |
|---|---|
| `COMPETENCE-DETAILLEE` | "Réaliser un storyboard" |
| `MACRO-SAVOIR-FAIRE` | "Animer une équipe" |
| `MACRO-SAVOIR-ETRE-PROFESSIONNEL` | "Faire preuve de créativité" |
| `SAVOIR` | "Photoshop", "Typographie" |

Doc API : https://francetravail.io/produits-partages/catalogue/rome-4-0-metiers/documentation

---

## Lancer la démo console

```bash
python liste_competences.py --input-dir output --output competences.csv
python competences_pair_elo.py
# a / b = choisir   = = égalité   espace = passer   q = quitter
```

---

## Cible

HTML + JS statique, déployable sur GitHub Pages. Zéro serveur.
