# Étape 3 — Chargement des données

## Objectif

Lire les 5 sources (CSV, Excel, JSON), les ranger au format commun, et dresser un premier inventaire de leurs anomalies.

**Livrable attendu (cahier des charges, §8) :** données brutes chargées et inventaire des anomalies initiales.

À cette étape, **on ne corrige rien**. Les valeurs sont renommées et rangées, mais gardées telles que la source les donne. La correction, c'est l'étape 4.

## Structure

Le dossier reprend `src/` et `tests/` de l'étape 2 et ajoute :

```
03step3_chargement/
├── src/
│   ├── main.py                     # charge les 5 sources et affiche l'inventaire
│   ├── constantes.py               # + DOSSIER_SOURCES
│   ├── loaders/
│   │   ├── load_csv.py             # lire_csv
│   │   ├── load_json.py            # lire_json
│   │   ├── load_excel.py           # lire_excel
│   │   ├── correspondances.py      # une table de renommage par source
│   │   └── harmonisation.py        # aplatir, harmoniser, charger_<source>
│   └── validation/
│       └── inventaire.py           # inventorier
└── tests/
    ├── test_loaders.py
    ├── test_harmonisation.py
    └── test_inventaire.py
```

## Exécution

Avec l'environnement virtuel activé, depuis `03step3_chargement/` :

```bash
python -m src.main         # charge les 5 sources et affiche l'inventaire
python -m pytest -v        # lance les 22 tests
```

Il faut utiliser `python -m` : il ajoute le dossier courant aux chemins de recherche de Python, ce qui rend `src` importable. `python src/main.py` échoue avec `ModuleNotFoundError: No module named 'src'`.

## Le principe : lire, puis harmoniser

```
fichier source ──lire──► lignes brutes (noms d'origine) ──harmoniser──► biens au format commun
```

Ces deux opérations sont séparées, car elles ne dépendent pas de la même chose :

| Opération | Dépend de | Fonctions |
|---|---|---|
| **Lire** | du **format** | `lire_csv`, `lire_json`, `lire_excel` : 3 fonctions |
| **Harmoniser** | de la **source** | `harmoniser` : 1 fonction, avec 5 tables de correspondance |

La plateforme, les notaires et l'historique sont trois CSV : ils utilisent la même fonction de lecture, avec un séparateur, un encodage et une table différents.

Chaque `charger_<source>()` renvoie une **liste de dictionnaires au format commun**, exactement comme le jeu d'essai des étapes 1 et 2. Les fonctions déjà écrites (`champs_manquants`, `ids_en_double`, les règles) s'appliquent donc directement aux vraies données.

## Les fonctions de lecture

| Fonction | Outil | Renvoie |
|---|---|---|
| `lire_csv(chemin, separateur, encodage)` | `csv.DictReader` | une liste de dictionnaires, une par ligne, avec les noms de colonnes d'origine |
| `lire_json(chemin)` | `json.load` | la liste d'annonces telle qu'elle est dans le fichier (imbriquée) |
| `lire_excel(chemin)` | `openpyxl` | une liste de dictionnaires, une par ligne de la feuille « Annonces » |

**Les types dépendent du format.** Un CSV est un fichier texte : toutes les valeurs sont lues comme des chaînes (`"320860000.0"`). Le JSON et l'Excel stockent de vrais nombres (`18152000`, `35.7`). Le chargement garde le type donné par le format, sans rien convertir. `convertir_prix` accepte déjà les deux cas.

## Les paramètres de chaque source

| Source | Fichier | Lecture | Séparateur | Encodage |
|---|---|---|---|---|
| plateforme | `plateforme_immo_sn.csv` | `lire_csv` | `;` | UTF-8 |
| agence | `agence_teranga.xlsx` | `lire_excel` | — | — |
| particuliers | `particuliers.json` | `lire_json`, puis `aplatir` | — | UTF-8 |
| notaires | `notaires.csv` | `lire_csv` | `,` | UTF-8 |
| historique | `import_historique.csv` | `lire_csv` | `;` | **latin-1** |

Ces paramètres sont écrits **dans** chaque `charger_<source>()`, pas passés par celui qui l'appelle : ce sont des propriétés de la source.

## L'harmonisation

`harmoniser(ligne, correspondances, source, valeurs_fixes=None)` :

1. crée un dictionnaire avec les 13 champs du format commun, tous à `None` ;
2. remplit `source` ;
3. copie chaque valeur de la ligne vers son champ commun, d'après la table de correspondance ;
4. ajoute les valeurs fixes ;
5. renvoie ce **nouveau** dictionnaire. La ligne d'origine n'est pas modifiée.

On part de 13 champs à `None` pour que **tous les biens aient exactement les mêmes clés**, quelle que soit leur source. Un champ que la source ne fournit pas existe quand même : il vaut `None`, et l'inventaire le compte.

Les colonnes qui ne correspondent à aucun champ commun ne sont pas gardées : `quartier`, `description` et `date_expiration` (plateforme), `Commercial` (agence).

**Pourquoi `valeurs_fixes=None` et pas `valeurs_fixes={}` ?**
Python crée la valeur par défaut **une seule fois**, quand il définit la fonction. Un dictionnaire par défaut serait partagé entre tous les appels : si la fonction le modifiait un jour, la modification resterait pour les appels suivants. La forme habituelle est `None`, remplacé par `{}` au début de la fonction.

### Les tables de correspondance

Une table par source, dans `correspondances.py`, au format **nom dans la source → nom commun**. Elles reprennent le tableau du README général.

### JSON : aplatir avant d'harmoniser

Les particuliers sont imbriqués : `annonce → details → prix`. La fonction récursive `aplatir` transforme chaque annonce en dictionnaire à un seul niveau :

```python
{"annonce": {"id": "PRT-01461", "localisation": {"region": "Fatick"}}}
# devient
{"annonce.id": "PRT-01461", "annonce.localisation.region": "Fatick"}
```

Quand une valeur est elle-même un dictionnaire, `aplatir` **s'appelle elle-même** avec le préfixe allongé. Elle traite ainsi n'importe quelle profondeur. Les clés obtenues sont les chemins de la colonne `chemin_json` du dictionnaire de données : la table de correspondance des particuliers les reprend telles quelles.

## Les champs déduits

Trois sources n'ont pas de colonne `type_transaction`, et une seule source donne la périodicité. Ces champs sont **traduits** depuis une information de la source, jamais devinés.

| Source | Champ | Règle | Justification |
|---|---|---|---|
| notaires, historique | `type_transaction` | toujours `"vente"` (`VALEURS_FIXES_VENTE`) | Décisions validées (voir README général) |
| agence | `type_transaction` | d'après le statut (`STATUT_VERS_TRANSACTION`) | Décision validée : « Disponible » et « Loué » sont des locations |
| plateforme | `periodicite` | `"mensuel"` si `devise` vaut `"FCFA/mois"`, sinon `None` | La source le dit explicitement |

Pour l'agence, la correspondance des statuts est :

| Statut | Nombre | Transaction |
|---|---|---|
| Vendu | 334 | vente |
| En vente | 198 | vente |
| Disponible | 61 | location |
| Loué | 47 | location |

Un statut absent de cette table donne `None` : il sera signalé plutôt que deviné.

**La devise de la plateforme** vaut `FCFA` pour les 698 ventes et `FCFA/mois` pour les 177 locations, sans aucune incohérence. Elle n'est pas renommée (ce n'est pas un champ commun), mais elle donne la périodicité. La plateforme est la seule source où elle est connue.

**La périodicité de l'agence et des particuliers reste vide.** Ces sources ont respectivement 108 et 219 locations, mais n'indiquent nulle part si le loyer est mensuel, trimestriel ou annuel. Écrire `"mensuel"` serait inventer une donnée. Elle reste `None` et sera signalée.

## L'inventaire des anomalies initiales

`inventorier(biens)` compte, **sans rien modifier** :

```python
{
    "lignes": ...,
    "ids_en_double": ...,                         # nombre d'identifiants présents plusieurs fois
    "manquants": {"prix": ..., "surface": ...},   # par champ ; un champ jamais manquant n'apparaît pas
    "regles": {"prix_positif": {"respectee": ..., "violee": ..., "non_evaluable": ...}, ...},
}
```

Elle ne lit aucun fichier et n'affiche rien : elle compte, c'est tout. On peut donc la tester sur le jeu d'essai.

**Pourquoi l'inventaire ne convertit rien avant de compter ?**
Il doit décrire les données **telles qu'elles sont chargées**. Convertir les prix avant de compter ferait passer `"à négocier"` pour une valeur manquante, alors que c'est une valeur illisible. Chaque règle fait ses propres conversions à l'intérieur de sa condition, sans toucher au bien.

### Les résultats

Sortie de `python -m src.main`, mise en tableau :

| Source | Lignes | ids en double | prix violé | prix non évaluable | Autres manquants |
|---|---|---|---|---|---|
| plateforme | 875 | 15 | 6 | 0 | surface 5 |
| agence | 640 | 0 | 5 | 0 | — |
| particuliers | 731 | 0 | 2 | 61 | surface 75 |
| notaires | 410 | 0 | 0 | 14 | salles_bain 410 |
| historique | 528 | 0 | 0 | 10 | ville 8, statut 528 |
| **Total** | **3 184** | **15** | **13** | **85** | |

`periodicite` n'est pas dans le tableau : elle est manquante pour toutes les ventes et pour les locations de l'agence et des particuliers.

Les règles `type_bien_reconnu` et `transaction_valide` sont respectées par tous les biens des 5 sources.

**Lecture :**
- **La qualité annoncée se vérifie.** Les notaires (« très bonne ») n'ont aucune violation ; les particuliers (« faible ») ont le plus de valeurs manquantes.
- **Les 2 prix violés des particuliers valent `"None FCFA"`.** Ce n'est pas un vide mais un texte illisible : il est classé « violé », pas « non évaluable ».
- **Les 15 identifiants en double de la plateforme** sont les lignes recopiées annoncées par le dictionnaire de données.

### Trois sortes de « manquants »

L'inventaire compte de la même façon des situations de nature différente :

| Cas | Exemple | Nature |
|---|---|---|
| La source n'a pas la colonne | `salles_bain` chez les notaires (410/410), `statut` dans l'historique (528/528) | Limite de la source |
| Sans objet | `periodicite` pour une vente | Pas une anomalie |
| Valeur vraiment absente | 61 prix chez les particuliers, 8 villes dans l'historique | Anomalie réelle |

Le rapport qualité de l'étape 4 devra les séparer.

## Les tests

22 tests : les 13 de l'étape 2, et 9 nouveaux.

| Fichier | Tests | Ce qu'ils vérifient |
|---|---|---|
| `test_loaders.py` | 3 | Chaque fonction de lecture : nombre de lignes, identifiant et prix de la première ligne, avec le type d'origine |
| `test_harmonisation.py` | 5 | Chaque source : nombre de biens, et un bien entier comparé à un dictionnaire attendu |
| `test_inventaire.py` | 1 | L'inventaire complet du jeu d'essai |

Les tests d'harmonisation comparent le **bien entier** (13 champs), écrit en dur à partir de la ligne source. Cette comparaison vérifie aussi qu'il n'y a pas de clé en trop : deux dictionnaires ne sont égaux que s'ils ont exactement les mêmes clés.

Cas couverts : une vente et une location pour la plateforme (périodicité `"mensuel"`) et pour l'agence (transaction déduite, périodicité `None`).

Le bien de location de l'agence est retrouvé par son identifiant (`next(...)`), pas par sa position dans le fichier.

### Ce que les tests ont attrapé pendant l'écriture

- **Un mauvais séparateur** (`;` au lieu de `,` pour les notaires) : le fichier avait toujours 410 lignes, mais chaque ligne était une seule colonne et tous les champs valaient `None`. Compter les lignes ne suffit pas à vérifier une lecture.
- **Des correspondances à l'envers** (nom commun → nom source) : les champs restaient à `None` et des clés en trop apparaissaient.
- **Une faute de casse** (`"statut"` au lieu de `"Statut"`) : les 640 biens de l'agence avaient `type_transaction = None`, sans aucun message d'erreur.

Dans les trois cas, Python ne signale rien : un `.get()` sur une clé absente renvoie `None`. Seule la comparaison avec un attendu complet l'a révélé.

## Limites connues

- **L'inventaire mélange les trois sortes de manquants** (voir ci-dessus).
- **Aucune règle ne vérifie encore les dates, les surfaces ou la géographie.** Les manquants sont comptés, mais une surface négative ou une date « hier » n'apparaissent pas encore comme violations. Ces règles seront ajoutées à l'étape 4.
- **`aplatir` n'a pas de test dédié.** Elle est vérifiée indirectement par le test des particuliers.
- **Les doublons sont comptés par identifiant uniquement.** Les doublons entre sources (même bien, identifiants différents) seront traités à l'étape 4 avec `cle_rapprochement`.
- **`main.py` affiche les dictionnaires bruts.** Une présentation en tableau viendra avec le rapport qualité.
