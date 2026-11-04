# Étape 5 — NumPy et Pandas

## Objectif

Analyser les biens propres avec NumPy et Pandas : statistiques descriptives, prix au mètre carré, résultats par groupe. Compléter aussi la validation avec les seuils d'atypie du cahier des charges (§6.2) qui manquaient encore.

**Règle de lecture (§5.4) :** les ventes et les locations ne sont **jamais mélangées**. Un prix de vente et un loyer mensuel ne se comparent pas.

## Structure

Le dossier reprend `src/` et `tests/` de l'étape 4, et ajoute ou modifie :

```
05step5_analyse/
├── src/
│   ├── main.py                     # + règle prix_m2_hors_fourchette
│   ├── analyse/
│   │   └── statistiques.py         # nouveau : DataFrame, statistiques, prix au m², groupes
│   ├── loaders/
│   │   └── load_csv.py             # + charger_referentiel_prix_m2
│   └── validation/
│       ├── regles.py               # + applicable, seuils en constantes, 4 nouvelles règles
│       └── inventaire.py           # + les 3 nouvelles règles de REGLES
└── tests/
    ├── test_statistiques.py        # nouveau
    ├── test_regles.py
    ├── test_inventaire.py
    └── test_loaders.py
```

`requirements.txt` ajoute `pandas==3.1.0` et `numpy==2.5.4`.

## Exécution

Avec l'environnement virtuel activé, depuis `05step5_analyse/` :

```bash
python -m src.main         # pipeline complet et rapport qualité
python -m pytest -v        # lance les 91 tests
```

Les fonctions d'analyse ne sont pas encore appelées par `main.py`. Elles seront utilisées dans le notebook de l'étape 6.

## Sur quelles données ?

Les analyses portent sur les **2 983 biens propres et uniques** produits par `executer_pipeline` : ni quarantaine, ni doublon exact. Les biens en quarantaine ont des valeurs absentes ou illisibles. Les garder fausserait les moyennes, et un doublon compterait le même bien deux fois.

| | Biens |
|---|---|
| Ventes | 2 534 |
| Locations | 449 |

## Morceau B : du dictionnaire au DataFrame

| Fonction | Rôle |
|---|---|
| `vers_dataframe(biens)` | liste de dictionnaires → DataFrame, une ligne par bien, une colonne par champ |
| `separer_transactions(df)` | renvoie `(ventes, locations)`, deux **copies** (`.copy()`) |

**Les types après conversion :** `prix` et `surface` sont des `float64`, puisqu'ils ont été convertis à l'étape 4. `salles_bain` est aussi un `float64`, alors que ce sont des entiers. La colonne contient 390 valeurs manquantes chez les biens propres, et un `int` NumPy ne peut pas valoir `NaN` : Pandas passe donc la colonne en `float`. `date` reste une chaîne ISO.

## Morceau C : les statistiques descriptives

`resumer(valeurs)` renvoie le nombre, la moyenne, la médiane, l'écart-type, le minimum, les quartiles Q1 et Q3, et le maximum. Le calcul est fait avec NumPy (`np.mean`, `np.median`, `np.std`, `np.percentile`).

- **Les valeurs manquantes sont retirées avant le calcul.** Avec un seul `NaN`, `np.mean` renverrait `NaN`.
- **Une liste vide** renvoie `nombre = 0` et `None` partout, et non une erreur.
- **L'écart-type utilise `ddof=1`** (écart-type d'échantillon). C'est la convention de Pandas, et un test vérifie que les deux bibliothèques donnent le même résultat. Par défaut, NumPy utilise `ddof=0`.

`statistiques_descriptives(df, colonnes=("prix", "surface"))` applique `resumer` à chaque colonne.

| | Nombre | Moyenne | Médiane | Écart-type | Min | Q1 | Q3 | Max |
|---|---|---|---|---|---|---|---|---|
| Prix de vente (FCFA) | 2 534 | 104,6 M | **74,7 M** | 98,2 M | 5,2 M | 38,8 M | 129,4 M | 567,6 M |
| Loyer (FCFA) | 449 | 417 962 | **325 000** | 319 231 | 40 000 | 185 000 | 550 000 | 1 755 000 |
| Surface vendue (m²) | 2 534 | 237 | 147 | 286 | 10 | 71 | 248 | 1 495 |

**Lecture :** la moyenne est nettement au-dessus de la médiane, pour les ventes (104,6 M contre 74,7 M) comme pour les loyers. La distribution est donc **étirée vers la droite** : quelques biens très chers tirent la moyenne vers le haut. La médiane est plus robuste, mais le cahier des charges demande les deux. L'écart entre elles est en lui-même une information sur la forme de la distribution.

## Morceau D : le prix au mètre carré

`ajouter_prix_m2(df)` renvoie une copie du DataFrame avec une colonne `prix_m2 = prix / surface`.

```python
np.where(surface > 0, prix / surface, np.nan)
```

**Pourquoi `np.where` ?** Avec Pandas, `100 / 0` ne lève pas d'erreur : il donne `inf`. Un seul `inf` rendrait la moyenne infinie. Une surface nulle, négative ou absente donne donc `NaN`, que `resumer` ignore.

**Le prix au m² n'est calculé que pour les ventes.** La périodicité des loyers est inconnue pour l'agence et les particuliers (étape 3). Un loyer au m² mélangerait des montants mensuels et des montants inconnus.

| Type de bien | Ventes | Médiane du prix au m² (FCFA) |
|---|---|---|
| Villa | 448 | 906 133 |
| Studio | 302 | 748 131 |
| Maison | 536 | 670 301 |
| Appartement | 590 | 656 661 |
| Local commercial | 144 | 625 691 |
| Chambre | 157 | 571 792 |
| Terrain | 357 | 64 765 |

Le terrain a un prix au m² environ dix fois plus bas que les autres catégories : sans construction, c'est attendu. Mélanger les terrains aux logements ferait baisser toutes les moyennes.

## Morceau E : les résultats par groupe

`resultats_par_groupe(df, colonne_groupe, colonne_valeur)` renvoie, pour chaque groupe, le **nombre**, la **moyenne** et la **médiane**, triés par médiane décroissante. C'est un seul `groupby(...).agg(...)`.

| Ville (ventes) | Ventes | Médiane du prix au m² (FCFA) |
|---|---|---|
| Dakar | 44 | 1 021 546 |
| Rufisque | 54 | 807 320 |
| Pikine | 42 | 780 855 |
| … | | |
| Ziguinchor | 69 | 508 005 |
| Keur Massar | 29 | 469 529 |

Par région, Dakar arrive aussi en tête, avec une médiane de 772 682 FCFA/m² sur 207 ventes.

**Les petits groupes sont affichés, avec leur nombre.** On ne les cache pas : le lecteur voit qu'une médiane calculée sur peu de biens est fragile. Sur les données actuelles, chacune des 46 villes a au moins 5 ventes.

**`count` compte les valeurs non manquantes**, pas les lignes. Pour `prix_m2`, `nombre` est donc le nombre de biens dont le prix au m² a pu être calculé.

## Morceau F : les seuils d'atypie du §6.2

L'étape 4 jugeait les loyers avec les seuils des ventes. 51 des 56 prix atypiques étaient des loyers normaux, sous 100 000 FCFA. Le §6.2 demande quatre contrôles de plus, avec des seuils **configurables**. Ils sont en constantes en tête de `regles.py` :

```python
LOYER_MIN, LOYER_MAX = 25_000, 5_000_000      # par mois
CHAMBRES_MAX_PETIT_LOGEMENT = 10              # appartement, studio
SALLES_BAIN_MARGE = 2                         # salles_bain > chambres + 2
TYPES_SANS_CHAMBRES = {"Local commercial", "Terrain"}
```

### Le paramètre `applicable`

`RegleValidation` reçoit un dernier paramètre : `applicable`, une fonction qui dit si la règle concerne ce bien. Si elle renvoie `False`, le résultat est **`non_evaluable`**, avant même de regarder la valeur.

Une vente n'est ni « respectée » ni « violée » pour une règle sur les loyers : elle n'est pas concernée. La compter comme respectée gonflerait le taux de conformité, puisque le taux ne doit porter que sur les biens concernés.

### Les règles

| Règle | Gravité | S'applique à | Condition « respectée » |
|---|---|---|---|
| `prix_atypique` (modifiée) | avertissement | **ventes** | 100 000 ≤ prix ≤ 2 000 000 000 FCFA |
| `loyer_atypique` | avertissement | **locations** | 25 000 ≤ loyer ≤ 5 000 000 FCFA |
| `chambres_atypiques` | avertissement | Appartement, Studio | chambres ≤ 10 |
| `salles_bain_atypiques` | avertissement | logements dont `chambres` est rempli | salles_bain ≤ chambres + 2 |
| `prix_m2_hors_fourchette` | avertissement | ventes d'une catégorie connue, avec prix et surface > 0 | prix au m² dans la fourchette de la catégorie |

**`salles_bain_atypiques` exclut les locaux commerciaux et les terrains.** La règle compare des salles de bain à des chambres, et n'a de sens que pour un logement. Un local commercial a 0 chambre par nature, et ses sanitaires ne sont pas des salles de bain d'habitation. Avant cette exclusion, 74 des 162 biens signalés étaient des locaux commerciaux. Un bien sans nombre de chambres est aussi non évaluable : on ne compare pas avec une valeur manquante.

**`prix_m2_hors_fourchette` est créée par une fonction** (`creer_regle_prix_m2_hors_fourchette(referentiel)`), comme `ville_region_coherentes`, car elle a besoin du référentiel des catégories.

### La fourchette du prix au m²

`referentiel_categories.csv` donne, par catégorie, un prix minimum et maximum **indicatif** et une surface minimum et maximum **typique**, mais pas de prix au m². `charger_referentiel_prix_m2()` en déduit les cas extrêmes :

- le m² le moins cher : `prix_min / surface_max` ;
- le m² le plus cher : `prix_max / surface_min`.

Pour un Appartement : 25 M / 180 m² ≈ 138 889, et 120 M / 45 m² ≈ 2 666 667 FCFA/m².

**Nous avons choisi cette fourchette large.** Une fourchette étroite (`prix_min / surface_min` à `prix_max / surface_max`) signalerait à tort une grande villa vendue à bas prix, ce qui est parfaitement possible. Les bornes du référentiel sont indicatives, et ne sont pas faites pour fixer un seuil précis.

**Limite :** la fourchette est très large. Son haut est 11 à 50 fois plus grand que son bas selon la catégorie, et **211 fois** pour le terrain (5 333 à 1 125 000 FCFA/m²). Seules 7 ventes sont signalées : la règle ne détecte que les incohérences grossières.

## Les résultats

Le rapport qualité de l'étape 4, avec les nouvelles règles :

| Règle | Violée | Non évaluable | Taux de conformité |
|---|---|---|---|
| `prix_atypique` | 3 (contre 56 à l'étape 4) | 573 | 99,9 % |
| `loyer_atypique` | 2 | 2 704 | 99,6 % |
| `chambres_atypiques` | 0 | 2 050 | 100 % |
| `salles_bain_atypiques` | 88 | 1 001 | 96,0 % |
| `prix_m2_hors_fourchette` | 7 | 630 | 99,7 % |

Ces nombres portent sur les 3 184 biens reçus, quarantaine et doublons compris.

| Indicateur | Étape 4 | Étape 5 |
|---|---|---|
| Conservés avec avertissement | 53 | **91** |
| Entièrement conformes | 1 839 (57,8 %) | **1 834 (57,6 %)** |
| Quarantaine | 187 | 187 |

**Lecture :**
- **Les loyers ne sont plus faussement atypiques.** Avec des seuils de loyer, 2 loyers sur 480 sont signalés, contre 51 avec les seuils de vente.
- **Le nombre de biens avec avertissement augmente quand même**, à cause de `salles_bain_atypiques` : 88 logements ont au moins 3 salles de bain de plus que de chambres (1 chambre et 4 salles de bain, par exemple). Ce sont des incohérences à vérifier, réparties dans les quatre sources qui ont des salles de bain : plateforme 29, particuliers 21, historique 20, agence 18.
- **La quarantaine ne change pas** : les quatre nouvelles règles sont des avertissements.

## Décisions de conception

**Analyse sur les propres uniques.** Les statistiques portent sur les 2 983 biens hors quarantaine et sans doublons exacts.

**Ventes et locations toujours séparées** (§5.4), et prix au m² calculé pour les ventes seulement, puisque la périodicité des loyers est inconnue.

**Une règle qui ne concerne pas un bien le déclare `non_evaluable`.** Le taux de conformité reste ainsi celui des biens concernés.

**`prix_atypique` ne juge plus que les ventes.** Les loyers ont leur propre règle, avec leurs propres seuils.

**Locaux commerciaux et terrains exclus de `salles_bain_atypiques`.** Ce ne sont pas des logements.

**Fourchette du prix au m² large**, déduite des cas extrêmes du référentiel. Elle produit peu de faux avertissements, mais détecte peu de choses.

## Les tests

91 tests : les 68 de l'étape 4 (certains mis à jour), et 23 nouveaux.

| Fichier | Nouveaux | Ce qu'ils vérifient |
|---|---|---|
| `test_statistiques.py` | 11 | DataFrame (9 lignes, 13 colonnes), séparation 7 ventes / 2 locations, `resumer` calculé à la main sur `[1, 2, 3, 4, 100]`, `NaN` et liste vide, médiane des ventes après pipeline, écart-type NumPy = Pandas, prix au m² (surface nulle → `NaN`, PLT-00002), copie non modifiée, groupes et tri |
| `test_regles.py` | 4 | `prix_m2_hors_fourchette` : dans la fourchette, hors fourchette, location, surface vide |
| `test_inventaire.py` | 7 | compteurs des nouvelles règles sur le jeu d'essai ; local commercial non évaluable ; appartement violé ; loyer d'une vente non évaluable ; loyer bas violé ; appartement de 12 chambres violé, villa non évaluable |
| `test_loaders.py` | 1 | fourchette du terrain, 7 catégories |

**Les valeurs attendues sont calculées à la main**, jamais avec la fonction testée. Une valeur attendue construite avec Pandas recopie le résultat de Pandas : le test ne peut plus échouer.

### Les erreurs trouvées pendant l'écriture

- **Un test d'écart-type sur les biens bruts** : `"26 620 000"` n'est pas un nombre, et le calcul plantait. Les statistiques se font après le pipeline.
- **Un test de tri qui ne pouvait pas échouer** : « Dakar » vient avant « Thiès » par médiane, mais aussi par ordre alphabétique, et `groupby` trie par ordre alphabétique. Sans `sort_values`, le test passait quand même. Les données ont été changées pour que les deux ordres diffèrent.
- **Un code changé pour faire passer un test** : le tri a ensuite été passé en croissant, contre la docstring, au lieu de corriger les données du test. Quand un test échoue, on cherche d'abord pourquoi.
- **Des champs inventés** : `update({"transaction": ..., "loyer": ...})` ajoutait deux clés que la règle ne lit pas. Le test passait, parce que le bien restait une vente, mais ne vérifiait rien. Comme à l'étape 4 (`date_publication`), un test doit pouvoir échouer.
- **Un attendu ajusté au résultat** : un test nommé `..._violee` attendait `"non_evaluable"`.
- **Un chargeur en double** : une copie dans `regles.py`, avec un chemin relatif au dossier courant. Il est resté dans `loaders/`.

## Limites connues

- **La fourchette du prix au m² est très large** (×211 pour le terrain) : elle ne détecte que les cas grossiers.
- **Les seuils de loyer supposent un loyer mensuel**, alors que la périodicité est inconnue pour l'agence et les particuliers.
- **Les fonctions d'analyse ne sont pas branchées dans `main.py`.** Elles le seront dans le notebook (étape 6).
- **Reprises de l'étape 4 :** la périodicité vide n'est pas signalée, les trois sortes de manquants ne sont pas séparées dans le rapport, et rien n'est exporté (étape 7).
