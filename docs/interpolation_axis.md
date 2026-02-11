# interpolation_axis.md

## But

Définir l’axe **1 → 9** de la “Matrice d’Interpolation” et la façon dont le moteur calcule une **position continue** (ex. 6.4) sur cet axe pour produire une réaction “interpolée” (émotions / mythes / événements). 

---

## Définition de l’axe (vertical)

La matrice mappe la réalité sur un axe vertical : 

* **1 (Sommet)** : Cerveau, Intellect, Unité cognitive. 
* **[2–8] (Spectre)** : Zone d’interpolation (émotions, mythes, événements). 
* **9 (Base)** : Plancher pelvien, Instinct, Fondation matérielle. 

---

## Variable “position sur l’axe”

On représente l’état d’un sujet par une position continue :

* `axis_pos ∈ [1.0, 9.0]`
* `axis_pos = 1.0` = cognition/intellect dominant
* `axis_pos = 9.0` = instinct/fondation dominant

### Interprétation simple (lecture “somatique”)

* plus `axis_pos` monte vers 1 → style analytique, abstrait, méta, “cortex”
* plus `axis_pos` descend vers 9 → style concret, impulsif, vital, “fondation”

---

## Zone d’interpolation [2–8]

Le cœur du comportement “âme artificielle” est l’interpolation dans **[2–8]** : 

* **2–4** : affectif / relationnel / régulation (bas-milieu)
* **5** : pivot (équilibre, neutralité, changement) — utile comme “point de bascule” 
* **6–8** : structuration / volonté / expansion (haut-milieu)

> Note : votre document “numérologie inversée” pose explicitement des dualités (9/1, 8/2, 7/3, 6/4) et **5** comme point d’équilibre. 

---

## Numérologie inversée vs Axe d’interpolation (séparation recommandée)

Pour éviter une collision de sens :

* **Axe d’interpolation (somatique)** : reste **1↔9** tel que défini dans le README. 
* **Archétype numérologique (inversé)** : sert à pondérer les traits/valeurs (ontologie), indépendamment de `axis_pos`. 

En clair :

* `axis_pos` pilote la *dynamique* (où l’agent “résonne” sur l’axe 1–9)
* `archetype_digit` pilote la *personnalité* (profil de traits)

---

## Calcul de l’axe (MVP)

### Entrées typiques

* signaux “cosmiques”/structurels (ex. placements Mars/Saturne) pour positionner le sujet sur l’axe 
* ou signaux internes (émotion, stress, fatigue) qui déplacent `axis_pos` au fil de la simulation

### Sorties

* `axis_pos` (float)
* `band` (catégorie) : `TOP (1–2)`, `SPECTRUM (2–8)`, `BASE (8–9)`
* `intensity` (0–1) : amplitude de la réponse
* `stability` (0–1) : inertie (résistance au changement de bande)

---

## Règles d’interpolation (simples)

### 1) Interpolation linéaire

* `w_top = (9 - axis_pos) / 8`
* `w_base = (axis_pos - 1) / 8`
* `w_spectrum = 1 - |axis_pos - 5| / 4` (clamp 0..1)

### 2) Interpolation par “bandes”

* si `axis_pos <= 2` → réponses dominées par cognition/abstraction
* si `2 < axis_pos < 8` → réponses dominées par narration/émotion/mythe
* si `axis_pos >= 8` → réponses dominées par instinct/pragmatisme

---

## Exemple d’usage dans le moteur

Le moteur instancie une “âme” et produit une réaction interpolée sur l’axe 1–9 (ex. selon Mars/Saturne) : 

* input : “Comment perçois-tu l’autorité ?”
* state : `axis_pos = 6.7` (spectre bas→structure)
* output attendu : réponse structurée, orientée règles/responsabilité, mais encore narrative/émotive (car dans [2–8])

---

## TODO / points bloquants

* Si l’archétype numérologique inversé est utilisé, compléter le **digit 2** dans `pi_ontology.json` (sinon trou de mapping via inversion). (documenté comme manquant dans le JSON; à corriger avant d’automatiser l’inversion.)
