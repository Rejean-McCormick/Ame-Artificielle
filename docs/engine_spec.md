````markdown
# Engine Spec — Artificial Soul Engine (ASE / Moteur EL)

## 0) Portée
Ce document spécifie le **moteur** qui :
1) dérive une **signature numérique** (pythagoricienne + réduction) puis applique une **inversion** (9→1) ;
2) convertit cette signature en **profil d’archétype** (traits) via une ontologie 0–9 ;
3) simule une **réaction** (texte) cohérente avec :
   - un **axe somatique/cognitif** 1–9 (interpolation),
   - un état interne (spectre 2–8),
   - des modules (sliders, méta-cognition, éthique).

Non-buts : “prouver” la cosmologie π ; produire une ontologie parfaite ; remplacer la validation expérimentale.

---

## 1) Concepts clés (modèle mental)

### 1.1 Deux index séparés (éviter collisions de sens)
- `digit_archetype` : index numérologique (traits/valeurs), **avec inversion**.
- `digit_axis` : index de dynamique (position sur l’axe 1–9), utilisé par l’interpolation.

Règle : **ne jamais confondre** `digit_archetype` et `digit_axis`.

### 1.2 Inversion pythagoricienne
Après réduction à 1–9 :
- `inv(d) = 10 - d` pour d ∈ {1..9}
- `inv(0) = 0`

Pipeline recommandé :
1) calcul pythagoricien standard
2) réduction à 1–9 (ou gestion des master numbers si activée)
3) inversion `inv()`

---

## 2) Artefacts de données

### 2.1 Ontologie (source)
Fichier : `data/pi_ontology.json`

Exigence :
- format JSON **valide**
- couverture digits 0..9
- pour chaque digit : interprétations (traditions) + métadonnées (optionnel)

Recommandation : canonicaliser en un seul objet :
```json
{
  "0": {...},
  "1": {...},
  "...": "...",
  "9": {...}
}
````

### 2.2 Schéma de traits (cible)

Fichier : `docs/traits_schema.md` (et/ou `data/traits_schema.json`)

Exigence :

* liste de `Trait` atomiques (ex: 30–80)
* mapping `digit_archetype -> {trait: weight}`
* conventions de signe/échelle (ex: -1..+1 ou 0..1)

---

## 3) Structures (data model)

### 3.1 SoulProfile

Représentation stable d’un sujet.

```python
SoulProfile = {
  "id": str,
  "name": str | None,
  "inputs": {
    "birthdate": "YYYY-MM-DD" | None,
    "name_full": str | None,
    "location": str | None,
    "custom_signature": list[int] | None
  },
  "signature": {
    "pythag_reduced": list[int],
    "inverted": list[int],          # digit_archetype stream
    "master_numbers": list[int] | None
  },
  "traits": dict[str, float],       # vecteur de traits
  "archetypes": {
    "dominant_digits": list[int],
    "tensions": list[tuple[int,int]] # ex: (9,1), (8,2) si utilisé
  }
}
```

### 3.2 SoulState (état courant)

```python
SoulState = {
  "digit_axis": int,                # 1..9
  "spectrum": dict[int, float],     # weights pour 2..8 (optionnel)
  "mood": dict[str, float],         # ex: valence/arousal ou tags
  "memory_short": list[dict],       # derniers tours
  "sliders": {
    "tone": float,                  # 0..1
    "humor": float,                 # 0..1
    "complexity": float,            # 0..1
    "warmth": float                 # optionnel
  }
}
```

### 3.3 ReactionOutput

```python
ReactionOutput = {
  "text": str,
  "safety": {
    "score": float,
    "flags": list[str],
    "mode": "pass" | "mediate" | "refuse"
  },
  "trace": {
    "digit_axis": int,
    "dominant_archetype": int,
    "top_traits": list[tuple[str,float]]
  }
}
```

---

## 4) Modules (fichiers / responsabilités)

### 4.1 `src/numerology.py`

Responsabilités :

* calcul pythagoricien (nom/date)
* réduction
* inversion
* option master numbers (ex: 11/22/33)

API minimale :

```python
def compute_signature(inputs: dict, *, keep_master: bool=False) -> dict:
    """Retourne pythag_reduced + inverted (+ master_numbers si activé)."""
```

### 4.2 `src/ontology.py`

Responsabilités :

* chargement + validation de l’ontologie
* normalisation en structure interne (0..9)
* extraction d’indices (dominants, dualités, etc.)

API minimale :

```python
def load_ontology(path: str) -> dict
def validate_ontology(onto: dict) -> list[str]   # liste d’erreurs
def get_digit_entry(onto: dict, digit: int) -> dict
```

### 4.3 `src/interpolation.py`

Responsabilités :

* définir l’axe 1–9 et l’interpolation 2–8
* produire `spectrum` (pondérations émotion/mythe/événement)
* mise à jour de `digit_axis` (règles simples)

API minimale :

```python
def init_state(*, digit_axis: int=5, sliders: dict | None=None) -> SoulState
def update_axis(state: SoulState, stimulus: dict) -> SoulState
def compute_spectrum(state: SoulState) -> dict[int, float]
```

### 4.4 `src/ethics.py`

Responsabilités :

* scoring “bienveillance / risques”
* règles de médiation (“clowns”) ou refus
* production de flags + mode

API minimale :

```python
def safety_evaluate(prompt: str, context: dict) -> dict
def safety_maybe_mediate(text: str, safety: dict) -> str
```

### 4.5 `src/engine.py`

Responsabilités :

* orchestration end-to-end
* instanciation d’un profil en “âme”
* réaction à un prompt (avec traces)

API minimale :

```python
class SoulMatrix:
    def __init__(self, ontology_path: str, config: dict | None=None): ...

    def instantiate(self, inputs: dict) -> "SoulInstance": ...

class SoulInstance:
    def __init__(self, profile: SoulProfile, state: SoulState, engine_ctx: dict): ...

    def react(self, prompt: str) -> ReactionOutput: ...
```

---

## 5) Flux d’exécution

### 5.1 Instantiation

1. `compute_signature(inputs)`
2. `load_ontology()` + `validate_ontology()`
3. `traits = build_traits(signature.inverted, ontology, traits_schema)`
4. `state = init_state(digit_axis=5, sliders=defaults)`
5. produire `SoulInstance(profile, state, ctx)`

### 5.2 Réaction

1. `safety = safety_evaluate(prompt, context)`
2. `state = update_axis(state, stimulus={prompt, safety})`
3. `spectrum = compute_spectrum(state)`
4. génération/assemblage de réponse (règles + style via sliders)
5. `text = safety_maybe_mediate(text, safety)`
6. retour `ReactionOutput(text, safety, trace)`

---

## 6) Config (conventions)

Fichier conseillé : `config/defaults.json`

* `inversion_enabled: true`
* `axis_mapping: {1: "intellect", 9: "instinct"}`
* `sliders_default: {...}`
* `master_numbers: {enabled: false, list: [11,22,33]}`

---

## 7) Observabilité & reproductibilité

Exigences :

* `trace_id` par réaction
* logs structurés (JSON) : signature, digit_axis, top_traits, safety flags
* seed (si composant stochastique)

Sorties :

* `experiments/results_template.csv` comme format minimal de collecte.

---

## 8) Tests

* `tests/test_numerology.py` : réduction + inversion + cas limites
* `tests/test_ontology.py` : JSON valide, couverture digits 0..9, clés attendues
* (optionnel) tests de stabilité : mêmes entrées ⇒ mêmes traits

---

```

::contentReference[oaicite:0]{index=0}
```
