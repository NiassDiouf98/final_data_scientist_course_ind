# Étape 1 — Python et structures de données

## Objectif

Manipuler des biens immobiliers avec les bases de Python (variables, conditions, boucles, fonctions, exceptions, listes, dictionnaires, tuples, ensembles).

**Livrable attendu (cahier des charges, §8) :** fonctions simples de filtrage, de vérification et de manipulation.

À cette étape, on ne lit pas encore les fichiers de `sources/`. On travaille sur un petit jeu d'essai écrit à la main.

## Fichiers

| Fichier | Contenu |
|---|---|
| `main.py` | Jeu d'essai, constantes, 6 fonctions, et essais affichés à l'écran |
| `test_main.py` | 8 tests automatiques (pytest) |

## Exécution

Depuis la racine du projet, avec l'environnement virtuel activé :

```bash
python3 step1_python_data_structure/main.py   # affiche les essais
pytest -v                                     # lance les 8 tests
```

Les essais de `main.py` sont placés sous `if __name__ == "__main__":`. Ils s'exécutent quand on lance le fichier, mais pas quand `test_main.py` l'importe.

## Le jeu d'essai

9 biens recopiés de **vraies lignes** des sources, au format commun (voir le README général). Chaque bien représente un cas précis :

| id_local | Source | Cas représenté |
|---|---|---|
| NOT-02192 | notaires | Bien correct (sans salles de bain : la source ne les fournit pas) |
| HIS-0001 | historique | Prix avec espaces : `"26 620 000"` |
| PLT-00002 | plateforme | Prix en millions : `"57.62 millions"` |
| HIS-0072 | historique | Prix absent (`"N/A"`), terrain avec 0 chambre |
| AGT-00836 | agence | Location déduite du statut « Disponible », périodicité inconnue, date `JJ/MM/AAAA` |
| PLT-00399 | plateforme | Location mensuelle |
| PLT-00080 | plateforme | Synonyme de catégorie : `"appart"` |
| PLT-00058 (×2) | plateforme | Identifiant en double (doublon exact présent dans le vrai fichier) |

Les valeurs sont recopiées **telles quelles** : aucune correction n'est faite à la main.

## Les notions Python et leur rôle

| Notion | Utilisation |
|---|---|
| Dictionnaire | Un bien ; la table `SYNONYMES` |
| Liste | Le jeu d'essai ; `CHAMPS_ATTENDUS` |
| Ensemble (set) | `CATEGORIES`, `VALEURS_VIDES`, identifiants déjà vus dans `ids_en_double` |
| Tuple | La clé renvoyée par `cle_rapprochement` |
| Conditions, boucles | `ids_en_double`, compréhensions de liste |
| Exceptions | `try/except ValueError` dans `convertir_prix` |

## Constantes

| Constante | Type | Contenu |
|---|---|---|
| `CATEGORIES` | set | Les 7 types de biens autorisés |
| `SYNONYMES` | dict | Écriture en minuscules → catégorie officielle (recopié de `referentiels/referentiel_categories.csv`) |
| `CHAMPS_ATTENDUS` | list | Les 13 champs du format commun |
| `VALEURS_VIDES` | set | Valeurs considérées comme « pas de valeur » : `None`, `""`, `"N/A"` |

## Les fonctions

| Fonction | Reçoit | Renvoie |
|---|---|---|
| `filtrer_par_transaction(biens, type_transaction)` | la liste, `"vente"` ou `"location"` | une **nouvelle** liste avec les biens correspondants |
| `champs_manquants(bien, champs_attendus)` | un bien | la liste des champs absents ou vides |
| `convertir_prix(prix)` | une valeur brute | un nombre, ou `None` si la valeur est vide ou illisible |
| `normaliser_type_bien(type_bien)` | un texte | la catégorie officielle, le texte d'origine s'il est inconnu, ou `None` |
| `ids_en_double(biens)` | la liste | l'ensemble des identifiants présents plusieurs fois |
| `cle_rapprochement(bien)` | un bien | le tuple `(type_bien, ville, surface, date)` |

## Choix et justifications

**La liste d'origine n'est jamais modifiée.**
Les fonctions renvoient de nouvelles valeurs. C'est le même principe que pour `sources/`, qui reste intact.

**« Manquant » = clé absente, `None`, `""` ou `"N/A"`, mais pas `0`.**
Un terrain a réellement 0 chambre : c'est une information, pas un trou. La fonction compare donc explicitement avec `VALEURS_VIDES` au lieu d'écrire `if not valeur`, qui aurait aussi considéré `0` comme manquant. Un test vérifie ce cas.

**Convertir n'est pas valider.**
`convertir_prix("0")` renvoie `0`. La fonction répond seulement à la question « ce texte est-il un nombre ? ». C'est une règle métier, à l'étape 4, qui mettra en quarantaine un prix ≤ 0. Garder les deux séparés permet de compter à part les erreurs de conversion et les violations de règles, comme le demande le cahier des charges (§7).

**Les prix en millions sont arrondis à l'unité.**
En Python, `66.74 × 1 000 000` donne `66739999.99999999`, car les nombres à virgule sont stockés en binaire. Le FCFA n'a pas de centimes : on arrondit à l'unité. Ce cas vient des vraies données de la plateforme et il est testé.

**Un type de bien inconnu est renvoyé tel quel.**
`normaliser_type_bien("Château")` renvoie `"Château"`, pas `None`. La fonction ne décide pas de la quarantaine. Garder la valeur d'origine permet d'écrire plus tard un motif précis (« type hors référentiel : Château »), et de distinguer un type **absent** d'un type **inconnu**. Pour savoir si un type est valide, on vérifie `type_bien in CATEGORIES`.

**Le texte est nettoyé avant d'être cherché dans les synonymes.**
On enlève les espaces aux bords et on met en minuscules, puis on cherche dans `SYNONYMES`. Il suffit donc d'une entrée par synonyme, quelle que soit la casse (`APPARTEMENT`, `Appartement`, `appartement`).

**Un set pour les identifiants déjà vus.**
Chercher dans un set est instantané, quelle que soit sa taille. Dans une liste, Python compare les éléments un par un. Sur les 3 224 lignes réelles, la différence devient importante.

**Un tuple pour la clé de rapprochement.**
Un tuple ne peut pas être modifié : Python accepte donc de le mettre dans un set ou d'en faire une clé de dictionnaire, ce qu'il refuse pour une liste.

**La clé de rapprochement utilise des valeurs normalisées.**
Sans normalisation, `"appart"` et `"APPARTEMENT"` donneraient deux clés différentes, et le même bien vu dans deux sources ne serait pas reconnu. La fonction réutilise `normaliser_type_bien`.

## Les tests

8 tests, qui couvrent les 6 fonctions avec des cas conformes, invalides et limites :

| Test | Ce qu'il vérifie |
|---|---|
| `test_filter_locations` | 2 locations dans le jeu d'essai |
| `test_champs_manquants` | HIS-0072 → `prix`, `periodicite`, `statut` ; `chambres` (= 0) n'est **pas** manquant |
| `test_convertir_prix_conformes` | nombre, espaces, suffixe FCFA, millions |
| `test_convertir_prix_limites` | `"66.74 millions"` (arrondi), `"0"` → `0` |
| `test_convertir_prix_invalides` | `"N/A"`, `"à négocier"`, `"None FCFA"` → `None` |
| `test_normaliser_type_bien` | casse, espaces, synonymes, type inconnu, `None` |
| `test_ids_en_double` | `{"PLT-00058"}` |
| `test_cle_rapprochement` | même clé malgré une casse et des espaces différents ; l'original n'est pas modifié |

Chaque test compare le résultat à une **valeur attendue écrite en dur**. Pour vérifier qu'ils détectent bien les erreurs, des bugs ont été introduits volontairement (suppression du traitement de « FCFA », remplacement de la condition de `champs_manquants` par `if not bien.get(champ)`) : les tests concernés ont échoué.

## Limites connues

- **Les dates ne sont pas normalisées.** `"24/07/2022"` et `"2022-07-24"` donnent des clés de rapprochement différentes. À traiter à l'étape 4.
- **Les villes accentuées ne sont pas rapprochées.** `"Mbacké"` et `"MBACKE"` donnent des clés différentes.
- **La surface doit être strictement égale.** Une tolérance (doublon « probable ») sera définie à l'étape 4.
- **Les synonymes sont recopiés à la main.** Ils seront lus depuis le référentiel à l'étape 3.
- `convertir_prix` gère seulement « millions » au pluriel et en minuscules, seule forme présente dans les données.

## Points reportés à l'étape 4

- **Périodicité « sans objet ».** Une vente n'a jamais de périodicité. `champs_manquants` la compte pourtant comme manquante. Le rapport qualité devra la classer comme « non évaluable » et non comme « manquante ».
- **Manquant ou erreur de conversion.** `"N/A"` (valeur manquante) et `"à négocier"` (erreur de conversion) donnent tous deux `None`. Le rapport devra les compter séparément.
