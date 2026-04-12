# Ranking algorithm — description
_Session du 2026-04-12_

---

## Principe général

Active learning ELO : on ne compare que les skills qui ont du pouvoir discriminant sur le classement courant. Converge beaucoup plus vite qu'un tirage aléatoire global.

---

## Algorithme (boucle principale)

```
1. score(job) = Σ  elo(skill) × weight(importance)
   weights : principal=3  standard=1  emergent=0.5

2. top_jobs = jobs triés par score → garder les 30 premiers
   (tous les jobs si aucun vote encore)

3. Tirer job_A et job_B au hasard dans top_jobs

4. Tirer skill_A ∈ job_A  et  skill_B ∈ job_B
   contraintes :
     - skill_A ≠ skill_B
     - skill_A ∉ job_B  ET  skill_B ∉ job_A   ← sinon le vote ne différencie pas les deux jobs
     - type ∈ { COMPETENCE-DETAILLEE, MACRO-SAVOIR-FAIRE, MACRO-SAVOIR-ETRE-PROFESSIONNEL }
       (exclure SAVOIR : "Photoshop vs InDesign" = comparaison nulle)

5. Présenter la paire à l'utilisateur, recueillir le vote (-2 / -1 / 0 / +1 / +2)

6. Mettre à jour elo(skill_A) et elo(skill_B) selon le score ELO standard
   K-factor = 32

7. Recalculer les scores de tous les jobs affectés
   → utiliser skill_jobs.json (index inversé skill → [jobs]) pour ne recalculer que les jobs concernés

8. Répéter depuis 2
```

---

## Condition d'arrêt

À définir — options :
- Nombre fixe de votes (ex: 20)
- Stabilité du top 10 (les 10 premiers ne changent plus)
- Bouton "voir les résultats" disponible dès N votes minimum (ex: 8)

---

## Structure de données (statique, générée par build_json.py)

```
skills.json     { code: { libelle, type, freq } }
jobs.json       { code: { libelle, principal:[codes], standard:[codes], emergent:[codes] } }
skill_jobs.json { code: [job_codes] }   ← index inversé pour les mises à jour ELO rapides
```

`freq` = proportion des métiers utilisant ce skill → utile pour filtrer les skills trop universels
ou trop rares si on veut un mode de sélection alternatif.

---

## État côté webapp (en mémoire, jamais persisté)

```js
elo = { skill_code: float }          // initialisé à 1500
scores = { job_code: float }         // recalculé après chaque vote
vote_count = int
```
