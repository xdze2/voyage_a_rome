# Design decisions — Voyage à Rome
_Session du 2026-04-12_

---

## Contexte de départ

Exploration de la base ROME 4.0 (France Travail, opendata).
Scripts Python existants : fetch API, extraction compétences, démo ELO console.
Objectif : transformer ça en POC web statique fun et partageable.

---

## Nom du projet

**Voyage à Rome** — jeu de mots avec la ville. "Tous les chemins mènent à Rome."

---

## Compréhension des données ROME

### Types de compétences (champ `type` dans les YAML)

| Type | Description | Exemple |
|---|---|---|
| `COMPETENCE-DETAILLEE` | Savoir-faire concret, formulé en action | "Réaliser un storyboard" |
| `MACRO-SAVOIR-FAIRE` | Capacité transversale large | "Animer une équipe" |
| `MACRO-SAVOIR-ETRE-PROFESSIONNEL` | Qualité comportementale | "Faire preuve de créativité" |
| `SAVOIR` | Connaissance théorique, outil, diplôme | "Photoshop", "Typographie" |

### Sections dans une fiche métier

- `competencesMobiliseesPrincipales` — cœur du métier
- `competencesMobilisees` — complémentaires
- `competencesMobiliseesEmergentes` — émergentes (ex: réalité augmentée)

Les compétences dans les `appellations` (variantes du titre de poste) ont une `frequence` (0–100) qui indique leur prévalence dans les offres d'emploi réelles.

---

## Décisions de conception

### 1. Périmètre des données

**Décision : données complètes (2 000 métiers)**

Estimation taille JSON statique :
- 30 000 compétences × ~100 octets ≈ 3 Mo brut → **~400 Ko gzippé**
- 2 000 métiers × (code + libelle + ~30 refs) ≈ 400 Ko brut → **~80 Ko gzippé**
- Total : < 1 Mo gzippé. Pas de problème.

Structure JSON retenue (séparation skills / jobs) :
```
skills.json   { "102727": { "libelle": "...", "type": "..." }, ... }
jobs.json     { "E1205": { "libelle": "Graphiste", "skills": ["102727", ...] }, ... }
```
Les métiers ne stockent que des codes — les libellés sont dans le dictionnaire skills.

### 2. Nombre de votes

**Décision : TBD, à expérimenter**

Le vrai problème n'est pas le nombre de votes mais **quelles compétences montrer**.
30 000 compétences à comparer deux à deux = ingérable.

Approche retenue : ne montrer que les compétences à **fort pouvoir discriminant**.
Critère : fréquence entre ~5 % et ~60 % des métiers.
— Trop universelles ("Faire preuve de rigueur") → ne discriminent rien, à exclure.
— Trop rares → pas assez de signal.

Avec ce filtre, estimation : **200–500 compétences utiles**.
Sur cet espace réduit, 20–30 votes commencent à converger.

### 3. Quels types de compétences montrer dans les votes

**Décision : COMPETENCE-DETAILLEE + MACRO-SAVOIR-ETRE dans les votes. SAVOIR dans les résultats uniquement.**

Raisonnement :
- `COMPETENCE-DETAILLEE` : formulées en action, concrètes, naturellement comparables
- `MACRO-SAVOIR-ETRE` : souvent révélateur du profil, bon candidat au vote
- `SAVOIR` : "Photoshop vs InDesign" = vote nul. Utile dans l'affichage de la fiche résultat, pas dans le jeu.

Option : exposer le filtre à l'utilisateur (case à cocher au départ).

### 4. Résultat affiché

**Décision : top 10 métiers + lien externe vers la fiche France Travail + 3–5 compétences qui expliquent le score**

- Lien gratuit : `https://candidat.francetravail.fr/metierscope/#/fiche-metier/{CODE}`
- Afficher les compétences du métier ayant le meilleur ELO chez l'utilisateur → répond à "pourquoi ce métier ?"

---

## Plan d'implémentation (ordre retenu)

1. **Script Python : YAML → JSON statique**
   - Lire tous les YAML de `output/` (puis full ROME)
   - Filtrer et indexer les compétences (discriminant, type)
   - Produire `skills.json` + `jobs.json`

2. **Frontend HTML/JS statique**
   - Chargement des JSON
   - Sélecteur de types de compétences (optionnel)
   - Boucle de votes (paires ELO)
   - Calcul et affichage du top 10 avec liens

3. **Déploiement GitHub Pages**
   - Dossier `docs/` ou `web/` à la racine

---

## Stack technique cible

- Données : JSON statique pré-généré
- Frontend : HTML + JS vanilla (ou framework léger)
- Hébergement : GitHub Pages
- Zéro backend, zéro auth, zéro infra
