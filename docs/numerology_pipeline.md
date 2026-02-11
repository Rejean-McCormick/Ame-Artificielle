## Contenu proposé — `Ame-Artificielle/docs/numerology_pipeline.md`

# Numerology Pipeline (Pythagoricien inversé)

## 0) Rôle du document

Ce fichier spécifie **comment dériver des chiffres (0–9)** à partir d’entrées (date, nom, etc.) pour alimenter le moteur ASE/EL, qui mappe les archétypes et réactions sur une échelle 0–9. 

---

## 1) Concepts et conventions

### 1.1 Deux “espaces de chiffres”

* **Digit externe (Pythagoricien standard)** : résultat de la méthode classique (réduction).
* **Digit interne (inversé)** : digit utilisé par votre **numérologie inversée**, où l’échelle va de **9 → 1**, avec dualités 9/1, 8/2, 7/3, 6/4, et **5** comme point d’équilibre. 

### 1.2 Traitement de l’axe 1–9 (interpolation)

Indépendamment du sens numérologique, l’ASE utilise une **Matrice d’Interpolation** sur un axe vertical :

* **1 : cerveau / intellect**
* **2–8 : spectre (émotions, mythes, événements)**
* **9 : instinct / fondation** 

Recommandation : garder cet axe comme **axe de simulation** (somatique/dynamique), et utiliser le digit interne comme **archétype/traits**.

---

## 2) Étapes du pipeline

### Étape A — Extraction brute

Entrées possibles (au minimum) :

* `birth_date` (YYYY-MM-DD)
* `name` (prénom/nom ou nom complet)

**A.1 Date**

* Calcul : somme des chiffres de la date (en ignorant séparateurs).
* Exemple : 2003-01-03 → 2+0+0+3+0+1+0+3 = 9

**A.2 Nom (Pythagoricien standard)**

* Conversion lettres→nombres via table Pythagoricienne classique (1–9)
* Somme, puis réduction

*(La table lettres→nombres est une constante de configuration dans le code, versionnée.)*

---

### Étape B — Réduction (digit externe)

Réduction vers un digit **1–9** (par somme itérative des chiffres).

Option “master numbers” (configurable) :

* si `keep_master_numbers=true`, conserver 11/22/33 avant inversion (sinon réduire jusqu’à 1–9).

---

### Étape C — Inversion (digit interne)

Définition :

* si d ∈ {1..9} : **inv(d) = 10 − d**
* si d = 0 : **inv(0) = 0** (réservé)

Cette inversion encode la lecture “9 → 1” décrite dans votre système. 

Table (externe → interne) :

* 1→9, 2→8, 3→7, 4→6, 5→5, 6→4, 7→3, 8→2, 9→1

---

## 3) Digit 0 (cas spécial)

Le système global utilise une échelle 0–9 , et l’ontologie décrit le **0** comme “potentiel/void/reset” selon traditions. 

Convention proposée :

* 0 n’est **pas** un résultat de réduction classique (sauf entrées nulles).
* 0 sert de **sentinel** (silence, reset, état liminal) côté moteur.

---

## 4) Liaison avec l’ontologie (`pi_ontology.json`)

* Le mapping “chiffre → traits/lectures” provient de l’ontologie multi-traditions.
* Attention : l’ontologie signale explicitement que le **2 est manquant**. 
  Avec l’inversion, cela peut casser l’archétype **interne 8** (car 8 interne ↔ 2 externe), selon votre config.

Exemple de cohérence “externe vs interne” :

* Le **9 externe** est décrit comme “spirituel/humanitaire” dans la tradition pythagoricienne. 
* Dans votre numérologie inversée, ce “pôle humanitarisme/compassion” est porté par le **1 interne**. 
  → Donc : `digit_interne=1` peut pointer vers le contenu “9 externe” si vous faites une vue inversée de l’ontologie.

---

## 5) Exemple complet (date seule)

Entrée :

* `birth_date = 2003-01-03`

Calcul :

1. Somme = 9
2. Réduction externe = 9
3. Inversion interne = 1

Interprétation (selon vos textes) :

* 1 interne : humanitarisme/compassion/renouveau 
* Dualité associée : 9↔1 avec 5 comme équilibre 

---

## 6) Format de sortie (contrat)

Sortie standardisée (objet) :

* `source_inputs`: {birth_date, name, …}
* `raw_sums`: {date_sum, name_sum, total_sum}
* `digit_external`: {value, reduction_steps, master_number_used?}
* `digit_internal`: {value, inversion_rule_version}
* `warnings`: [ex. “digit 2 missing in ontology”, “master number reduced”, …]

---

## 7) Tests minimum

* Test inversion : 1↔9, 2↔8, 3↔7, 4↔6, 5↔5
* Test date : parsing stable (format, zéros)
* Test cohérence : `digit_internal` toujours dans {0..9}
* Test warning : si digit_internal==8 alors signaler possible dépendance au “2” manquant 
