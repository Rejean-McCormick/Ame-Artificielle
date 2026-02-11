# McCormick Protocol (MVP)
**But / Objectif** : tester si l’Artificial Soul Engine (ASE) produit des profils suffisamment distincts et cohérents pour être **reconnus** (matching) sans information contextuelle, au-delà du hasard.

Ce protocole est inspiré d’une idée de type “McCormick” déjà mentionnée dans la spec : association en aveugle de cartes anonymisées à des profils contrastés. 

---

## 1) Hypothèse & métriques

### 1.1 Hypothèse testable
**H1** : un évaluateur humain (ou un classifieur) peut associer une *carte de personnalité* à la bonne *signature* avec une précision significativement supérieure au hasard.

**H0** : les associations ne sont pas meilleures qu’un tirage aléatoire.

### 1.2 Métriques
- **Top-1 accuracy** : % de matchs exacts.
- **Top-k accuracy** (optionnel) : la bonne signature est dans les k meilleures propositions.
- **Temps de décision** (optionnel) : secondes / item.
- **Score de confiance** (optionnel) : 1–5.

### 1.3 Baseline (hasard)
Pour N profils :
- hasard top-1 = `1/N`
- hasard top-k = `k/N`

---

## 2) Matériel requis

### 2.1 Profils (signatures)
Préparer **N signatures** (ex. N=10, 20, 30) avec contraste volontaire :
- signatures “fortes” (dominance d’un archétype)
- signatures “mixtes”
- signatures “opposées” (ex. paires 9↔1, 8↔2, etc. si vous utilisez l’inversion) 

### 2.2 Cartes (output ASE)
Pour chaque signature, générer une **carte de personnalité** standardisée (voir 3.1).

### 2.3 Évaluateurs
- **Humains** (idéal) : 10–50 personnes.
- **Ou** un classifieur simple (logistic regression, etc.) si vous avez des features.

---

## 3) Format standard d’une “carte”

### 3.1 Template (identique pour toutes les cartes)
Chaque carte contient exactement :
1) **Tagline** (1 phrase)
2) **Forces** (5 bullets)
3) **Ombres / risques** (5 bullets)
4) **Style de communication** (ton, humour, complexité) — sliders 
5) **Réactions typiques** (3 mini-scénarios)
6) **Valeurs / motivations** (3 bullets)

> Interdiction : dates, noms, indices directs.

---

## 4) Procédure expérimentale (double aveugle léger)

### 4.1 Génération & anonymisation
1) Générer N cartes à partir des N signatures.
2) Remplacer les IDs par des codes : `CARD_01..CARD_N` et `SIG_A..SIG_N`.
3) Mélanger l’ordre.

### 4.2 Tâche de matching
Pour chaque carte, l’évaluateur doit :
- sélectionner la signature correspondante (1 parmi N)
- indiquer confiance (optionnel)
- (optionnel) top-k : donner 3 choix

### 4.3 Contrôle de biais
- Mélanger l’ordre des cartes par évaluateur
- Interdire discussion entre évaluateurs
- (optionnel) ajouter **cartes “nuisance”** générées aléatoirement pour vérifier la sensibilité

---

## 5) Analyse

### 5.1 Statistique simple
- Calculer top-1 accuracy globale et par évaluateur.
- Comparer à `1/N` (hasard) via test binomial ou permutation.

### 5.2 Analyse qualitative
- Quelles paires sont confondues ?
- Les confusions suivent-elles vos dualités (9↔1, etc.) ? 
- Les erreurs se concentrent-elles sur les profils mixtes ?

---

## 6) Critères de succès (MVP)
Exemples (à ajuster) :
- top-1 accuracy ≥ 2× hasard
- stabilité : pas seulement 1–2 évaluateurs “très bons”
- cohérence : cartes jugées “distinctes” par feedback

---

## 7) Fichiers de sortie recommandés
- `experiments/results_template.csv` : un log par essai
- `experiments/report.md` : synthèse, graphiques, décisions

---

## 8) Variantes rapides (si besoin)
- **N petit** (ex. 6) pour itérer vite.
- **A/B** : comparer “ASE avec inversion” vs “ASE sans inversion”.
- **Ablation** : enlever sliders / enlever méta-cognition / enlever ontologie multi-traditions.

