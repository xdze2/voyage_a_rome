# UI/UX design decisions
_Session du 2026-04-12_

---

## Principes directeurs

- Style **dry** : sobre, sans fioriture, pas de couleur superflue
- Ton **léger / second degré** dans les labels
- **Mobile-first** : colonne unique, max-width 720px centré
- Animations **minimalistes** : physique plutôt qu'effets

---

## Layout général

- Page en **colonne unique** centrée (max-width 720px)
- Pas de séparation horizontale (ni header, ni footer bordés)
- Footer positionné **directement sous le contenu** (pas en bas de page)
- Fond uniforme `#f7f5f0` — pas de surfaces blanches en header

---

## Header

- Titre en **Playfair Display** (serif expressif, 2rem) — côté éditorial / cartographique
- **ROME en capitales** espacées pour souligner l'acronyme
- Emoji 🏛️ devant le titre (Panthéon — référence visuelle à Rome)
- Sous-titre : explication complète du sigle ROME + pitch en une ligne
- Disclaimer vie privée dans le footer (pas dans le header)

---

## Vue comparaison

### Structure des boutons

```
[ compétence A ]  [ compétence B ]
[ ✌️ les deux ]  [ 😱 aucun ]  [ 🤔 je passe ]
```

- Les deux boutons principaux ont la **même taille et le même style** — pas d'influence sur le choix
- Pas de code couleur (gauche/droite ne sont pas orientés)
- Les 3 boutons secondaires ont le **même traitement visuel** que les principaux

### Labels des boutons secondaires

| Action | Label | Emoji | Signification algo |
|---|---|---|---|
| Les deux | `les deux, volontiers` | ✌️ | les deux skills montent |
| Aucun | `ni l'un ni l'autre` | 😱 | les deux skills descendent |
| Passer | `je passe` | 🤔 | aucune mise à jour ELO |

### Type de compétence

- Affiché en petit au-dessus du libellé : `emoji + texte` (ex: `🛠️ savoir-faire`)
- Même taille et style sur les deux boutons → ne biaise pas le choix

| Type ROME | Emoji | Label |
|---|---|---|
| `COMPETENCE-DETAILLEE` | 🛠️ | savoir-faire |
| `MACRO-SAVOIR-FAIRE` | 🧩 | savoir-faire |
| `MACRO-SAVOIR-ETRE-PROFESSIONNEL` | 🧠 | savoir-être |
| `SAVOIR` | 📚 | connaissance |

### Barre de progression

- Barre fine (6px) en haut, couleur accent (rouge)
- Texte : `encore N avant les résultats` → `prêt !` à MIN_VOTES
- Bouton `voir les résultats →` apparaît dans la barre une fois MIN_VOTES atteint

---

## Animations

| Déclencheur | Animation | Valeurs |
|---|---|---|
| Clic sur un bouton | `scale(0.97)` | 120ms — effet "enfoncement" physique |
| Nouvelle paire | `fly y:+6px + fade` | 200ms — glissement vers le haut |

Choix délibéré : **physique uniquement**, pas de flash couleur, pas de rebond.

---

## Footer

- Deux lignes, aligné à gauche :
  - `données ROME 4.0 · France Travail · POC`
  - `Aucune donnée collectée — tout reste dans votre navigateur.`
- Padding top généreux (3rem) pour respirer après le contenu

---

## Typographie

- Corps : `system-ui, -apple-system, sans-serif` — natif, rapide, lisible
- Titre : `Playfair Display, Georgia, serif` — chargé via Google Fonts
- Taille boutons principaux : `1.15rem / font-weight 500`
- Taille boutons secondaires : `1rem / font-weight 500`
- Uniformité : tous les boutons ont le même weight et la même taille de base

---

## Palette

```
--bg:       #f7f5f0   fond général (légèrement chaud)
--surface:  #ffffff   boutons
--border:   #d8d4cc
--text:     #1a1a1a
--text-muted: #888
--accent:   #c0392b   rouge Rome (barre de progression, bouton résultats)
```
