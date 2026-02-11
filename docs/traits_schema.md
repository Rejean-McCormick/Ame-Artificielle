# Traits Schema (MVP)

Ce document définit **le schéma de traits** (dimensions de personnalité) et comment une **signature numérologique** est convertie en **vecteur de traits** pour l’Artificial Soul Engine. :contentReference[oaicite:0]{index=0}

---

## 1) Conventions

### 1.1 Numérologie inversée (règle)
On utilise la numérologie **pythagoricienne**, puis on applique une inversion des digits :

- `inv(0) = 0`
- `inv(d) = 10 - d` pour `d ∈ {1..9}`

> Exemple : 9 → 1 ; 1 → 9.

### 1.2 Deux index (recommandé)
Pour éviter les collisions de sens :

- `d_archetype` : digit **archétype** (numérologie inversée) → **traits**
- `d_axis` : digit **axe d’interpolation** (1..9) → **dynamique somatique/cognitive** de la Matrice 0–9 (1=intellect, 9=instinct). :contentReference[oaicite:1]{index=1}

---

## 2) Liste des traits (canon)

Définir une liste de traits atomiques (20–60). Format recommandé :

- `trait_id` (string)
- `label`
- `description`
- `polarity` (optionnel : + / -)
- `scale` : [-2..+2] ou [0..1]

### Exemple de set minimal (24 traits)
**Cognition**
- `curiosity`, `analysis`, `abstraction`, `focus`, `flexibility`

**Affect**
- `empathy`, `emotional_stability`, `joy`, `anger`, `fear`, `compassion`

**Social**
- `leadership`, `cooperation`, `diplomacy`, `assertiveness`, `social_openness`

**Volition / Structure**
- `discipline`, `order`, `risk_taking`, `adaptability`, `responsibility`

**Spiritualité / Sens**
- `intuition`, `meaning_seeking`, `transcendence`, `altruism`

---

## 3) Format de mapping digit → traits

Chaque digit `d_archetype` (0–9) a un profil :

- **Tagline**
- **Forces**
- **Ombres**
- **Règles de style** (sliders : ton/humour/complexité) :contentReference[oaicite:2]{index=2}
- **Poids de traits** (table)

### Format table (exemple)
| trait_id | weight |
|---|---:|
| empathy | +2 |
| leadership | -1 |

---

## 4) Profils archétypaux (numérologie inversée)

Ces définitions servent de baseline (à harmoniser avec `pi_ontology.json`). :contentReference[oaicite:3]{index=3} :contentReference[oaicite:4]{index=4}

### 9 — Indépendance / Leadership / Initiative
Dualité : 9 ↔ 1 ; 8 ↔ 2 ; 7 ↔ 3 ; 6 ↔ 4 ; 5 pivot. :contentReference[oaicite:5]{index=5}

### 8 — Coopération / Équilibre / Diplomatie / Dualité
⚠️ Vérifier cohérence avec l’ontologie (le “2” est manquant dans le fichier source, ce qui peut impacter des remaps). :contentReference[oaicite:6]{index=6}

### 7 — Expression / Communication / Créativité / Inspiration

### 6 — Stabilité / Organisation / Discipline / Structure

### 5 — Liberté / Changement / Aventure / Exploration (pivot/neutralité) :contentReference[oaicite:7]{index=7}

### 4 — Harmonie / Responsabilité / Amour / Équilibre domestique

### 3 — Spiritualité / Intuition / Contemplation / Recherche de sens

### 2 — Abondance / Matérialisation / Pouvoir / Transformation
⚠️ À consolider : votre ontologie actuelle indique une absence d’information sur le digit 2. :contentReference[oaicite:8]{index=8}

### 1 — Humanitarisme / Compassion / Générosité / Renouveau

---

## 5) TODO (pour rendre le fichier “exécutable”)
1) Fixer la **liste finale des traits** (+ définitions).
2) Écrire les **poids** par digit (manuellement d’abord).
3) Harmoniser `pi_ontology.json` avec l’inversion (ou générer une vue “inversée” à la volée). :contentReference[oaicite:9]{index=9}
4) Compléter le **digit 2** (sinon trous de mapping). :contentReference[oaicite:10]{index=10}
