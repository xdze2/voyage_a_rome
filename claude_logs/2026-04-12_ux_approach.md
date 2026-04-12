# UX / Game approach — décision
_Session du 2026-04-12_

---

## Options considérées

**Option 1 — Pair ranking**
Comparer des compétences deux à deux → score ELO → top 10 métiers.
Simple, fun, rapide. Pas de notion de niveau.

**Option 2 — Individual ranking avec niveau**
L'utilisateur note chaque compétence (jamais / débutant / confirmé / expert).
Plus proche d'un CV helper. Données : skills + jobs + pondération par niveau.

**Option 3 — Double ranking présent / futur**
"Ce que je fais aujourd'hui" vs "ce que je veux faire demain".
Écart de compétences = plan de formation potentiel. UX complexe.

---

## Décision

**Option 2, avec mode "pair rapide" intégré.**

- Mode rapide : compare des paires (fun, ~2 min) — option 1 comme sous-mode
- Mode détaillé : note chaque compétence individuellement (~10 min)
- Les deux produisent le même output : top 10 métiers + explication du score

Option 3 (présent/futur) laissée pour plus tard — faisable sans refonte, c'est juste une deuxième session de notation.

---

## Implications sur les données JSON

Champs à extraire des fiches YAML :

| Champ | Utilité |
|---|---|
| `code` | identifiant skill / job |
| `libelle` | affiché à l'utilisateur |
| `type` | grouper (savoir-faire / savoir-être / savoirs) |
| importance (principale / standard / émergente) | pondérer le score |

Champs à ignorer : `riasec`, `formacodes`, `contextesTravail`, `transitionEcologique`, appellations détaillées, tout le bruit des fiches.

---

## Structure JSON cible

```
data/dist/
├── skills.json   { "102727": { "libelle": "...", "type": "COMPETENCE-DETAILLEE", "freq": 0.12 } }
└── jobs.json     { "E1205": { "libelle": "Graphiste", "principal": [...], "standard": [...], "emergent": [...] } }
```

`freq` dans skills = % des métiers qui utilisent cette compétence → permet au webapp de sélectionner des paires discriminantes (exclure les trop universelles et les trop rares).
