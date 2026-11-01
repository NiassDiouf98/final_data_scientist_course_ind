# Étape 2 — Programmation modulaire et POO

## Objectif

Réorganiser le code de l'étape 1 en modules séparés, et introduire une classe pour représenter les règles métier.

**Livrable attendu (cahier des charges, §8) :** modules séparés, fonctions réutilisables, au moins une classe utile.

Le comportement des fonctions de l'étape 1 ne change pas. Elles sont seulement rangées dans des fichiers selon leur rôle. Les fichiers de `sources/` ne sont toujours pas lus : c'est l'objet de l'étape 3.

## Structure

```
02step2_POO/
├── src/                        # le code du pipeline
│   ├── constantes.py           # valeurs partagées par tous les modules
│   ├── loaders/                # étape 3 : chargement des sources (vide pour l'instant)
│   ├── processing/
│   │   └── traitement.py       # transformer les valeurs
│   └── validation/
│       ├── validation.py       # vérifier un bien ou une liste de biens
│       └── regles.py           # la classe RegleValidation et les règles métier
└── tests/
    ├── jeu_essai.py            # les 9 biens de l'étape 1
    ├── test_traitement.py
    ├── test_validation.py
    └── test_regles.py
```

Chaque dossier contient un fichier `__init__.py`. Il indique à Python que le dossier est un **package**, c'est-à-dire un ensemble de modules qu'on peut importer avec un point : `src.validation.regles`.

## Exécution

Avec l'environnement virtuel activé :

```bash
cd 02step2_POO
python -m pytest -v        # lance les 12 tests de l'étape 2
```

Depuis la racine du projet, `pytest -v` lance les tests des étapes 1 et 2 (20 tests).

`python -m pytest` ajoute le dossier courant aux chemins où Python cherche les modules. C'est ce qui permet d'écrire `from src.constantes import ...` dans le code et dans les tests.

## Rôle de chaque module

| Module | Contenu | Question à laquelle il répond |
|---|---|---|
| `constantes.py` | `VALEURS_VIDES`, `CHAMPS_ATTENDUS` | Quelles valeurs tout le monde partage ? |
| `processing/traitement.py` | `SYNONYMES`, `filtrer_par_transaction`, `convertir_prix`, `normaliser_type_bien`, `cle_rapprochement` | Comment transformer une valeur ? |
| `validation/validation.py` | `CATEGORIES`, `champs_manquants`, `ids_en_double` | Qu'est-ce qui manque ou se répète ? |
| `validation/regles.py` | `RegleValidation`, `prix_positif`, `type_bien_reconnu`, `transaction_valide`, `REGLES` | Le bien respecte-t-il les règles métier ? |

Le détail des fonctions reprises de l'étape 1 est dans [le README de l'étape 1](../01step1_python_data_structure/README.md).

## Sens des imports

```
constantes  ←  traitement  ←  validation / regles
```

Un module importe seulement ceux qui sont **à sa gauche**. `constantes` n'importe rien, `traitement` importe `constantes`, et `regles` importe les deux autres.

Ce sens unique évite les **imports circulaires** : si A importe B et que B importe A, Python ne peut charger ni l'un ni l'autre.

Deux autres règles :
- **Tous les imports partent de la racine de l'étape** : `src.` pour le code, `tests.` pour les tests. Un import raccourci comme `from constantes import ...` fonctionne parfois dans l'éditeur, mais échoue avec pytest.
- **`src/` n'importe jamais `tests/`.** Le pipeline doit fonctionner sans les tests. Les tests dépendent du code, jamais l'inverse.

## La classe `RegleValidation`

### Pourquoi une classe ?

Le cahier des charges impose des règles métier (prix positif, type de bien reconnu, transaction valide…). Chaque règle a toujours les mêmes informations :

| Attribut | Rôle | Exemple |
|---|---|---|
| `nom` | Identifier la règle dans le rapport qualité | `"prix_positif"` |
| `champ` | Le champ du bien à vérifier | `"prix"` |
| `motif` | Le message écrit en cas de quarantaine | `"Le prix doit être supérieur à zéro"` |
| `condition` | Une fonction qui reçoit la valeur et répond oui ou non | `_prix_est_positif` |

Une classe regroupe ces 4 informations dans un seul objet, avec une seule méthode, `verifier(bien)`, qui s'applique de la même façon à toutes les règles. Pour ajouter une règle, il suffit de créer un nouvel objet et de l'ajouter à la liste `REGLES` : la méthode `verifier` ne change pas.

Le bien, lui, reste un dictionnaire. Il circule simplement entre les fonctions, et en faire une classe n'apporterait rien à cette étape.

### Une fonction passée en paramètre

`condition` est une **fonction** stockée comme attribut. On la passe sans parenthèses :

```python
prix_positif = RegleValidation("prix_positif", "prix", "Le prix doit être supérieur à zéro", _prix_est_positif)
```

Avec des parenthèses, `_prix_est_positif()` serait appelée immédiatement, et c'est son résultat qui serait stocké. Sans parenthèses, on stocke la fonction elle-même, et `verifier` l'appelle plus tard avec `self.condition(valeur)`.

### Les trois résultats de `verifier`

| Résultat | Quand | Ce qu'il devient |
|---|---|---|
| `"non_evaluable"` | La valeur est vide (`None`, `""`, `"N/A"`) ou le champ est absent | Compté à part dans le rapport qualité (§7) |
| `"respectee"` | La condition répond oui | Le bien passe |
| `"violee"` | La condition répond non | Le bien part en quarantaine avec le `motif` |

**Pourquoi un prix illisible donne « violée » et non « non évaluable » ?**
`"à négocier"` n'est pas une valeur vide : la source a écrit quelque chose, mais ce n'est pas un prix. Le cahier des charges dit « normaliser si possible, sinon quarantaine ». Si ce cas était classé « non évaluable », ces annonces échapperaient à la quarantaine. La condition renvoie donc toujours `True` ou `False`, et seule une valeur vide donne « non évaluable ».

**Pourquoi pas de `try/except` dans `verifier` ?**
`convertir_prix` gère déjà ses erreurs attendues (un texte qui n'est pas un nombre). Une erreur dans une condition serait donc un **bug**. Un `try/except` le cacherait en le transformant en « non évaluable », sans message, et des biens seraient mal classés. Sans lui, le bug s'affiche immédiatement.

### Les règles déjà écrites

| Objet | Champ | Condition |
|---|---|---|
| `prix_positif` | `prix` | Le prix converti existe et est supérieur à 0 |
| `type_bien_reconnu` | `type_bien` | Le type normalisé fait partie des 7 catégories |
| `transaction_valide` | `type_transaction` | La valeur est `"vente"` ou `"location"` |

Les fonctions de condition commencent par `_` (`_prix_est_positif`…). C'est une convention Python : ces fonctions sont internes au module et ne doivent pas être utilisées ailleurs. On utilise les objets règles, pas leurs conditions.

## Les tests

12 tests : les 8 de l'étape 1, répartis selon les modules, et 4 nouveaux pour les règles.

| Fichier | Tests |
|---|---|
| `test_traitement.py` | 6 tests de l'étape 1 (filtrage, prix, type de bien, clé de rapprochement) |
| `test_validation.py` | 2 tests de l'étape 1 (champs manquants, identifiants en double) |
| `test_regles.py` | 4 nouveaux tests, détaillés ci-dessous |

| Test | Bien utilisé | Résultat attendu |
|---|---|---|
| `test_prix_positif_respectee` | PLT-00002 (`"57.62 millions"`) | `"respectee"` |
| `test_prix_positif_non_evaluable` | HIS-0072 (`"N/A"`) | `"non_evaluable"` |
| `test_prix_positif_violee_sur_une_copie` | copie de PLT-00002 avec `"à négocier"` | `"violee"` |
| `test_type_bien_reconnu_violee_sur_une_copie` | copie de PLT-00080 avec `"Château"` | `"violee"` |

Les cas modifiés travaillent sur une **copie** (`.copy()`) : le jeu d'essai n'est jamais modifié, sinon un test pourrait changer le résultat d'un autre.

Pour vérifier que ces tests détectent les erreurs, la vérification des valeurs vides a été retirée volontairement de `verifier` : `test_prix_positif_non_evaluable` a échoué.

## Limites connues

- **`transaction_valide` n'est pas encore testée.**
- **Les règles ne sont pas encore appliquées à une liste de biens.** Il n'existe pas encore de fonction qui parcourt `REGLES`, sépare les biens valides de la quarantaine et compte les résultats. Ce sera fait à l'étape 4.
- **Il manque des règles du cahier des charges** (surface positive, région et ville connues, cohérence prix / transaction…). Elles seront ajoutées à l'étape 4, quand les vraies données seront chargées.
- Les limites de l'étape 1 restent valables : dates non normalisées, villes accentuées, synonymes recopiés à la main.
