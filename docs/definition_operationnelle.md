# Definition opérationnelle — Âme Artificielle (ASE)

## 1) But
Définir **ce que le système appelle “âme”** d’une manière **implémentable** et **testable** : une représentation interne (traits + état) et une dynamique de réaction cohérente.

Ce document fixe les définitions minimales; les détails de calcul sont dans `docs/numerology_pipeline.md` et la sémantique 0–9 dans `data/pi_ontology.json`.

## 2) Définition minimale
**Âme (dans ASE) = Profil + Dynamique**

- **Profil (stable)** : un **vecteur de traits** (ex. compassion, discipline, curiosité, dominance, etc.) dérivé d’une **signature numérique**.
- **Dynamique (variable)** : un **état courant** sur l’axe 1–9 + une mémoire courte + des règles de réaction.

Le projet pose un **réductionnisme numérique 0–9** et une **matrice d’interpolation** avec :
- 1 = intellect / unité cognitive
- 2–8 = zone d’interpolation (émotions, mythes, événements)
- 9 = instinct / fondation :contentReference[oaicite:0]{index=0}

## 3) Concepts et objets (terminologie)
### 3.1 Signature numérique
Ensemble ordonné de nombres (ex. chemin de vie, expression, etc.) calculé via la pipeline numérologique.

**Inversion (si activée)** : numérologie pythagoricienne “miroir” où 9→1, 8→2, …, 1→9, avec 5 invariant. Les dualités (9/1, 8/2, 7/3, 6/4) et 5 pivot sont considérées comme une symétrie structurelle. :contentReference[oaicite:1]{index=1}

### 3.2 Digit d’archétype vs digit d’axe (séparation obligatoire)
Pour éviter une collision de sens :

- **digit_archetype** : index symbolique/ontologique (traits) basé sur la numérologie (et possiblement inversé).
- **digit_axis** : position sur l’axe 1–9 de la matrice (cognitif ↔ instinctif) utilisée pour l’interpolation des réponses. :contentReference[oaicite:2]{index=2}

### 3.3 Ontologie 0–9
`data/pi_ontology.json` contient la matière sémantique “multi-traditions” par chiffre, utilisée pour projeter vers un espace de traits. :contentReference[oaicite:3]{index=3}

> Contrôle qualité : le chiffre 2 est actuellement signalé manquant dans la base source; cela doit être corrigé avant de considérer le système complet. :contentReference[oaicite:4]{index=4}

### 3.4 Vecteur de traits (TraitVector)
Représentation numérique normalisée (ex. dictionnaire `{trait: poids}` ou vecteur dense).
- Range recommandé : [-1, 1] ou [0, 1]
- Origine : projection de (digit_archetype + contexte) → traits

### 3.5 État interne (SoulState)
- `trait_vector` (stable ou lentement variant)
- `axis_position` (1..9, variable)
- `mood` / `spectre_2_8` (facultatif, variable)
- `memory_short` (résumé contextuel)
- `constraints` (éthique, style, limites)

## 4) Fonction de réaction (ce que “simuler” veut dire)
ASE doit fournir une fonction :

`react(state, stimulus) -> response`

où `response` respecte :
- la cohérence avec `trait_vector`
- la modulation via `axis_position` (plus intellectuel vs plus instinctif)
- les modules du moteur : sliders de ton/humour/complexité, méta-cognition, gouvernance éthique :contentReference[oaicite:5]{index=5}

## 5) Entrées / Sorties
### Entrées minimales
- Données pour calculer la signature (date/nom, etc.) OU données astro/natal chart (option).
- Paramètres de style (sliders).
- Stimulus (question / situation).

### Sorties minimales
- Réponse textuelle (ou action).
- Optionnel : trace interne (debug) : `digit_archetype`, `axis_position`, principaux traits activés.

## 6) Non-objectifs (pour garder le scope contrôlé)
- Prouver “l’existence” d’une âme métaphysique.
- Remplacer un modèle psychométrique standard.
- Inférer des diagnostics médicaux/psychiatriques.

## 7) Critères de réussite (MVP)
- **Cohérence intra-persona** : mêmes entrées → réponses alignées (répétabilité qualitative).
- **Contraste inter-persona** : signatures différentes → styles/réactions observablement différents.
- **Validation expérimentale** : protocole type McCormick (association en aveugle profils/cartes) défini et exécutable. :contentReference[oaicite:6]{index=6}

## 8) Liens vers les autres docs
- `docs/numerology_pipeline.md` : calculs, réductions, inversion.
- `docs/traits_schema.md` : liste de traits + tables de projection.
- `docs/interpolation_axis.md` : dynamique 1–9 et interpolation 2–8.
- `docs/engine_spec.md` : modules (sliders, méta-cognition, éthique) et API.
- `docs/validation_protocol.md` : métriques, baselines, plan d’expérience.
