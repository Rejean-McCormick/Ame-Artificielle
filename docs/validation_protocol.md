# Validation Protocol — Protocole McCormick (ASE)

## 1) Objectif
Valider expérimentalement (et statistiquement) l’hypothèse suivante :
> Une IA, en aveugle, peut associer une carte du ciel anonymisée à un profil de personnalité correspondant, au-delà du hasard.

## 2) Hypothèses
- **H0 (nulle)** : la performance du système n’est pas meilleure qu’un tirage au hasard (ou qu’un baseline simple).
- **H1 (alternative)** : la performance est significativement supérieure au hasard.

## 3) Matériel (données)
### 3.1 Ensemble de sujets (S)
Chaque sujet doit avoir :
- Identifiant interne (ex. `S_0001`)
- Données astro/numérologie nécessaires au calcul (date/heure/lieu, ou équivalent)
- Un **profil texte** (biographie + traits) rédigé **sans** inclure les données natal/numérologie

Recommandations :
- Taille minimale MVP : N ≥ 30 (mieux : 50–200)
- Diversité : âges, cultures, domaines, sexes, tempéraments
- Ajouter un sous-ensemble “contrastes forts” (pour tester la sensibilité)

### 3.2 Cartes du ciel anonymisées (C)
Pour chaque sujet :
- Générer un objet `NatalChartFeatures` (format JSON) contenant uniquement des features autorisées.
- Retirer : nom, URL, texte biographique, indices évidents (ex. “Stockholm”, si trop unique), tout identifiant direct.

## 4) Contrôles anti-fuite (leakage)
Checklist obligatoire :
- Aucune mention de nom/personne dans les features.
- Aucune donnée biographique dans les features.
- Les prompts de test ne contiennent pas d’indices hors chart/features.
- Séparation stricte entre : (A) génération des profils, (B) génération des cartes, (C) évaluation.

## 5) Design expérimental (en aveugle)
### 5.1 Tâche principale : Matching K-choix
Pour chaque essai :
1) Sélectionner une carte anonymisée `C_i`.
2) Sélectionner un ensemble de K profils candidats `{P_1..P_K}`, incluant le vrai.
3) Donner à l’IA : `C_i` + la liste des profils candidats (texte), dans un ordre aléatoire.
4) L’IA doit retourner :
   - `predicted_profile_id`
   - `confidence` (0–1)
   - (optionnel) `rationale` (court, contrôlé)

K recommandé :
- MVP : K=3 ou K=5
- Ensuite : K=10

### 5.2 Répétitions
- Chaque `C_i` doit être évaluée sur plusieurs ensembles de candidats (ex. 10 tirages) pour estimer une distribution de performance.
- Random seed fixe pour reproductibilité (et noté dans les logs).

### 5.3 Split (si vous entraînez/ajustez quelque chose)
- `train` / `dev` / `test` (le test ne sert qu’une fois)
- Si pas d’entraînement, conservez quand même un “holdout” pour éviter l’optimisation inconsciente.

## 6) Baselines (obligatoires)
- **Hasard** : performance attendue = 1/K.
- **Heuristique simple** : ex. règle basée sur 1–2 features (pour vérifier si une fuite existe).
- (Optionnel) Classifieur non-LLM : logistic regression / random forest sur features numériques.

## 7) Métriques
- Accuracy top-1 (global)
- Accuracy top-k (si vous faites classement)
- Log-loss / Brier score (si confidence)
- Matrice de confusion (par sous-groupes)
- Effet vs hasard : `accuracy - 1/K`

## 8) Tests statistiques
- **Test binomial** (top-1) vs probabilité 1/K
- **Permutation test** (recommandé) : permuter les labels profils et recalculer la métrique
- Correction multi-tests si vous comparez plusieurs variantes (Bonferroni ou FDR)

Rapporter :
- p-value
- intervalle de confiance (bootstrap)
- taille d’effet

## 9) Robustesse / Ablations
- Ablation par famille de features (retirer Mars/Saturne, retirer maisons, etc.)
- Variantes numérologiques :
  - pythagoricien standard vs inversé
  - réduction différente (si applicable)
- Vérification “base-invariance” si vous exploitez π / séquences de chiffres (éviter artefacts base-10)

## 10) Traçabilité (reproductibilité)
À logguer pour chaque essai :
- date/heure
- seed
- version du modèle
- version des prompts
- config (ex. `inversion_enabled`, `standard_model`)
- input hash (chart/features)
- output (prediction + confidence)
- durée/latence (optionnel)

## 11) Sorties (fichiers)
- `experiments/results_template.csv` : table des essais (1 ligne = 1 trial)
- `experiments/run_manifest.json` : configuration + seeds + versions
- `experiments/summary.md` : résultats agrégés + figures (si utiles)

## 12) Critères de succès (MVP)
- Performance > hasard avec p < 0.05
- Effet stable sur plusieurs seeds / tirages de candidats
- Aucun signal évident de fuite (baseline heuristique ≈ hasard)

## 13) Limites et éthique
- Interprétations : éviter de présenter les résultats comme des diagnostics médicaux.
- Profils extrêmes/historiques : documenter les biais possibles, et garder le protocole centré sur la méthode.
