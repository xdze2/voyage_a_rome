# Algo — pistes d'amélioration
_Session du 2026-04-12_

---

## Problème : convergence trop lente

Chaque vote ne met à jour que 2 skills sur ~7776. La variance des scores de métiers monte très lentement. Avec 250 métiers et ~30 votes, le classement ne se stabilise pas suffisamment.

---

## Reformulation de l'algorithme (clarifiée en session)

```
1. Prendre les N meilleurs métiers (top-N par score ELO)
2. Choisir une catégorie aléatoire (type de skill OU contexte de travail)
3. Dans cette catégorie, trouver 2 métiers ayant des items exclusifs
4. Présenter un item de chaque → vote A/B
5. Mettre à jour les scores → reboucler
```

La clé : la sélection par **catégorie d'abord** rend tous les types de données (compétences, contextes de travail) comparables dans le même flux. Pas de phase séparée nécessaire.

---

## Pistes identifiées

### 1. RIASEC (endpoint `/metiers`)

Les métiers ont `riasecMajeur` / `riasecMineur` (Holland codes : R-I-A-S-E-C).
Les compétences détaillées ont aussi leurs propres codes RIASEC.

**Idée** : faire 6 questions Holland rapides avant les comparaisons de compétences pour initialiser les scores de métiers. Convergence immédiate dès le départ, avant même le premier vote de compétence.

**Endpoint à utiliser** : `/v1/metiers/metier` (plus approprié que `/fiche_metiers` pour les métadonnées).

### 2. Hiérarchie des compétences (endpoint `/competences`)

`CompetenceDetaillee` a un champ `macroCompetence` (parent).
Un vote sur un skill détaillé peut propager (avec K réduit) à son parent macro-compétence.
→ Un vote touche beaucoup plus de métiers → convergence plus rapide.

Le champ `codeArborescence` donne la structure hiérarchique complète.
À fetcher une fois et stocker dans un fichier JSON léger (quelques centaines de macros).

### 3. Contextes de travail (endpoint `/situations-travail`)

6 catégories discriminantes :

| Catégorie | Ce que ça distingue |
|---|---|
| `CONDITIONS_TRAVAIL` | Risques physiques, extérieur/intérieur |
| `LIEU_ET_DEPLACEMENT` | Mobilité, télétravail |
| `HORAIRE_ET_DUREE_TRAVAIL` | Horaires décalés, temps partiel |
| `TYPE_BENEFICIAIRE` | Contact enfants, clients, patients... |
| `TYPE_STRUCTURE_ACCUEIL` | Grande entreprise, TPE, indépendant |
| `STATUT_EMPLOI` | CDI, libéral, intérim... |

Ces contextes sont intégrés dans le même flux de comparaison (catégorie tirée au sort comme les types de compétences).
À vérifier : sont-ils déjà présents dans les YAML téléchargés ou nécessitent-ils un fetch séparé ?

---

## Priorités envisagées

| Priorité | Action | Prérequis |
|---|---|---|
| Court terme | Vérifier si contextes de travail sont dans les YAML existants | Lire un YAML brut |
| Court terme | Ajouter `riasecMajeur` dans `jobs.json` via `/metiers` | Fetch léger |
| Moyen terme | Fetch hiérarchie compétences → propagation ELO parent | Nouveau endpoint |
| Moyen terme | Intégrer contextes de travail dans le pool de paires | Nouveau endpoint ou YAML |
| Long terme | Quiz RIASEC 6 questions pour initialiser les scores | UX à concevoir |

---

## Note sur les endpoints API ROME

- `/metiers` : métadonnées métiers (RIASEC, domaine, flags transition, appellations proches)
- `/fiche_metiers` : compétences par métier structurées par enjeu — ce qu'on télécharge déjà
- `/competences` : hiérarchie des compétences (macro → détaillée), RIASEC par compétence
- `/situations-travail` : contextes de travail avec 6 catégories
