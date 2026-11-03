# Étape 4 — Validation et nettoyage

## Objectif

Corriger ce qui peut l'être sans ambiguïté, appliquer les règles métier, mettre en quarantaine ce qui ne peut pas être corrigé, détecter les doublons, et mesurer la qualité des données.

**Livrable attendu (cahier des charges, §8) :** données traitées, données en quarantaine et rapport de qualité.

Les fichiers de `sources/` ne sont jamais modifiés. Les biens en quarantaine sont gardés **tels que la source les donne**.

## Structure

Le dossier reprend `src/` et `tests/` de l'étape 3, et ajoute ou modifie :

```
04step4_validation/
├── src/
│   ├── main.py                     # pipeline complet + affichage du rapport
│   ├── constantes.py               # + DOSSIER_REFERENTIELS, STATUTS
│   ├── loaders/
│   │   └── load_csv.py             # + charger_referentiel_geographique
│   ├── processing/
│   │   └── traitement.py           # + convertir_surface, convertir_date,
│   │                               #   normaliser_selon_referentiel, nettoyer_bien
│   └── validation/
│       ├── regles.py               # + gravite, obligatoire, 7 nouvelles règles
│       ├── separation.py           # separer_biens
│       ├── doublons.py             # detecter_doublons
│       └── rapport.py              # produire_rapport
└── tests/
    ├── test_separation.py
    ├── test_doublon.py
    └── test_rapport.py
```

## Exécution

Avec l'environnement virtuel activé, depuis `04step4_validation/` :

```bash
python -m src.main         # exécute le pipeline et affiche le rapport qualité
python -m pytest -v        # lance les 68 tests
```

## Le principe : normaliser, puis valider

```
bien brut ──nettoyer_bien──► bien nettoyé ──règles──► propre / quarantaine ──doublons──► biens uniques
                │                                │                              │
                └──────────── journal (une entrée par bien) ────────────────────┴──► rapport qualité
```

L'ordre compte. Une date `"24/07/2022"` n'est pas au format ISO : validée **avant** nettoyage, elle serait rejetée. Or le format JJ/MM/AAAA est normalisable (`regles_metier.md`). Après nettoyage, elle vaut `"2022-07-24"` et la règle est respectée. C'est le cas d'AGT-00836 dans le jeu d'essai.

Chaque anomalie tombe dans une des trois catégories de `regles_metier.md` :

| Catégorie | Traitement | Exemple |
|---|---|---|
| **Normalisable** | corrigée, et la correction est notée dans le journal | `"26 620 000"` → `26620000` |
| **Bloquante** | le bien part en quarantaine avec un motif | prix `"à négocier"` |
| **Avertissement** | le bien est conservé, l'anomalie est signalée | prix de 50 000 FCFA |

## Morceau A : les conversions

Toutes les fonctions de conversion renvoient la valeur convertie, ou `None` si elle est vide ou illisible. Elles ne lèvent jamais d'exception.

| Fonction | Accepte | Exemple |
|---|---|---|
| `convertir_prix` (étape 1) | nombres, espaces de milliers, suffixe `millions` | `"57.62 millions"` → `57620000` |
| `convertir_surface` | nombres, virgule décimale, espaces | `"85,5"` → `85.5` |
| `convertir_date` | `AAAA-MM-JJ` et `JJ/MM/AAAA` | `"24/07/2022"` → `"2022-07-24"` |
| `normaliser_selon_referentiel` | une valeur et la liste des valeurs officielles | `"dakar "` → `"Dakar"` |

**`convertir_date` renvoie une chaîne ISO**, pas un objet `date`. Le bien reste ainsi un dictionnaire de valeurs simples, comparable et exportable tel quel en CSV ou en JSON.

**`normaliser_selon_referentiel` ne touche qu'à la casse et aux espaces.** Une valeur inconnue (`"Paris"`) est gardée telle quelle : c'est la règle `ville_region_coherentes` qui la signale. On ne corrige pas sans preuve.

**Le référentiel est passé en paramètre.** `charger_referentiel_geographique()` lit le fichier une fois, renvoie `{ville: region}` (46 villes), et ce dictionnaire est donné aux fonctions qui en ont besoin. Elles restent pures et testables sans fichier.

## Morceau B : `nettoyer_bien`

`nettoyer_bien(bien, villes, regions, statuts)` renvoie `(bien_nettoye, champs_corriges, erreurs_conversion)`. Le bien d'origine n'est pas modifié.

| Champ | Conversion |
|---|---|
| `prix`, `surface` | `convertir_prix`, `convertir_surface` |
| `date` | `convertir_date` |
| `type_bien` | `normaliser_type_bien` (synonymes) |
| `ville`, `region`, `statut` | `normaliser_selon_referentiel` |
| `chambres`, `salles_bain` | `int()` |

- **`champs_corriges`** : les champs dont la valeur a changé (`"appart"` → `"Appartement"`).
- **`erreurs_conversion`** : les champs qui avaient une valeur, mais qu'on n'a pas pu lire (`"à négocier"`, `"32/13/2024"`).

**Pourquoi distinguer une valeur vide d'une valeur illisible ?** `"N/A"` dit « je ne sais pas ». `"à négocier"` dit autre chose qu'un prix. Le rapport doit les compter séparément : le premier dans les manquants, le second dans les erreurs de conversion.

## Morceau C : les règles

La classe `RegleValidation` de l'étape 2 reçoit deux attributs :

| Attribut | Rôle |
|---|---|
| `gravite` | `"bloquante"` (quarantaine) ou `"avertissement"` (signalé) |
| `obligatoire` | si `True`, une valeur vide donne `"violee"` ; sinon `"non_evaluable"` |

La condition reçoit maintenant **le bien entier**, et non plus une seule valeur. Une règle peut ainsi croiser deux champs : la date et le statut, ou la ville et la région.

| Règle | Champ | Gravité | Obligatoire | Condition |
|---|---|---|---|---|
| `prix_positif` | prix | bloquante | oui | prix > 0 |
| `surface_positive` | surface | bloquante | oui | surface > 0 |
| `date_valide` | date | bloquante | oui | date ISO valide |
| `id_present` | id_local | bloquante | oui | identifiant non vide |
| `transaction_valide` | type_transaction | bloquante | oui | `vente` ou `location` |
| `type_bien_reconnu` | type_bien | bloquante | non | une des 7 catégories |
| `date_non_future_si_vendu` | date | bloquante | non | si le statut est Vendu, Vente conclue ou Acte signé : date ≤ aujourd'hui |
| `prix_atypique` | prix | avertissement | non | 100 000 ≤ prix ≤ 2 000 000 000 FCFA |
| `surface_atypique` | surface | avertissement | non | 5 ≤ surface ≤ 2 000 m² |
| `ville_region_coherentes` | ville | avertissement | non | la ville est dans le référentiel, avec cette région |

**Le même bien peut donner deux résultats différents.** HIS-0072 a le prix `"N/A"`. Pour `prix_positif`, qui est obligatoire, il est **violé** : on ne garde pas un bien sans prix. Pour `prix_atypique`, qui ne l'est pas, il est **non évaluable** : on ne peut pas dire si un prix absent est atypique.

**`ville_region_coherentes` est créée par une fonction** (`creer_regle_ville_region(referentiel)`), car sa condition a besoin du référentiel. C'est une **fermeture** : la fonction intérieure se souvient du référentiel reçu par la fonction extérieure. Elle n'est donc pas dans `REGLES` : c'est l'appelant qui l'ajoute, avec `REGLES + [creer_regle_ville_region(referentiel)]`.

## Morceau D : `separer_biens`

`separer_biens(biens, regles, villes, regions, statuts)` renvoie `(propres, quarantaine, avertissements, journal)`.

Pour chaque bien :
1. `nettoyer_bien` ;
2. chaque erreur de conversion devient un motif de quarantaine, sauf pour `chambres` et `salles_bain`, qui ne sont pas dans la liste des bloquantes et deviennent des avertissements ;
3. chaque règle est vérifiée **une seule fois** sur le bien nettoyé. Une bloquante violée ajoute son motif, **sauf si son champ est déjà en erreur de conversion** ;
4. avec au moins un motif, le bien **brut** va en quarantaine ; sinon, le bien nettoyé va dans les propres ;
5. une entrée est ajoutée au journal.

**Pourquoi le bien brut en quarantaine ?** La personne qui relit la quarantaine doit voir ce que la source a écrit. Dans le bien nettoyé, `"à négocier"` est devenu `None` : on ne saurait plus si le prix était vide ou illisible.

**Pourquoi un seul motif par champ ?** Pour `"à négocier"`, « prix illisible : 'à négocier' » décrit le problème. « Le prix doit être présent et supérieur à zéro » serait trompeur : personne n'a écrit de prix négatif.

**Le journal** contient une entrée par bien reçu : ses corrections, ses erreurs de conversion, ses avertissements, le résultat de chaque règle, et s'il est en quarantaine. Le rapport compte tout à partir de là, sans jamais compter un bien deux fois.

## Morceau E : `detecter_doublons`

Le cahier des charges (§6.1) demande de distinguer trois cas :

| Cas | Définition | Traitement |
|---|---|---|
| **Doublon exact** | même source, même `id_local`, tous les champs identiques | un exemplaire est gardé, les autres sont comptés |
| **Conflit** | même source, même `id_local`, valeurs différentes | aucun n'est gardé : `main.py` les met en quarantaine (« Conflit d'identifiant ») |
| **Doublon probable** | même `cle_rapprochement`, identifiants différents | **tous sont gardés**, et le groupe est signalé |

`detecter_doublons(biens)` s'applique aux **propres** : les biens en quarantaine ont des valeurs peu fiables, on ne les compare pas.

**La clé de rapprochement est `(type_bien, ville, surface, type_transaction)`.** La date en a été retirée. Chez les notaires, c'est la date de l'acte ; sur la plateforme, celle de la mise en ligne. Un même bien n'a donc pas la même date dans deux sources. Avec la date dans la clé, aucun doublon probable n'était trouvé sur les vraies données. `type_transaction` a été ajouté, car une vente et une location ne sont pas la même annonce.

**On ne fusionne pas les doublons probables** (`regles_metier.md` : « ne pas fusionner sans justification »). Une partie des 8 paires trouvées ressemble à des coïncidences, avec par exemple 1 chambre d'un côté et 6 de l'autre. Comme elles sont seulement signalées, un faux positif ne coûte qu'une vérification manuelle. Une clé trop stricte, à l'inverse, rate les vrais doublons sans rien dire.

## Morceau F : `produire_rapport`

`produire_rapport(biens, journal, doublons_exacts, conflits, doublons_probables, inventaire)` renvoie un dictionnaire avec les indicateurs du §7.

| Indicateur | Calcul |
|---|---|
| Taux de conformité d'une règle | respectées / **évaluables** × 100 (évaluables = respectées + violées) |
| Taux de doublons exacts | lignes en trop / biens reçus × 100 |
| Entièrement conformes | ni quarantaine, ni avertissement, ni correction ; taux sur les biens reçus |

**Les non-évaluables sont comptés à part**, et jamais comme conformes (§7). Une règle sans aucun bien évaluable a un taux `None`, et non une division par zéro.

**La définition d'« entièrement conforme » est stricte.** Elle mesure la qualité des sources **telles qu'elles arrivent**. Si on acceptait les corrections, le taux passerait de 57,8 % à 92,5 % : ce second chiffre mesure plutôt ce que le pipeline a réussi à sauver.

## Les résultats

Sortie de `python -m src.main` sur les 3 184 biens :

| Indicateur | Valeur |
|---|---|
| Biens reçus | 3 184 |
| Mis en quarantaine | 187 (5,9 %) |
| Conservés avec avertissement | 53 |
| Corrigés | 1 216 |
| Entièrement conformes | 1 839 (**57,8 %**) |
| Doublons exacts | 14 (0,4 %) |
| Conflits d'identifiant | 0 |
| Doublons probables (signalés) | 8 |
| Biens propres après dédoublonnage | 2 983 |

**Erreurs de conversion :** 8 prix (`"à négocier"`, `"None FCFA"`), 6 dates (`"32/13/2024"`), 4 surfaces (`"quatre-vingt"`).

**Motifs de quarantaine :**

| Motif | Biens |
|---|---|
| Prix absent ou ≤ 0 | 90 (85 absents, 5 négatifs ou nuls) |
| Surface absente ou ≤ 0 | 84 (80 absentes, 4 négatives) |
| Prix illisible | 8 |
| Date illisible | 6 |
| Surface illisible | 4 |
| Date future pour un bien vendu | 1 |

6 biens ont deux motifs : ni prix exploitable, ni surface.

**Quarantaine par source :**

| Source | Reçus | Quarantaine | Taux |
|---|---|---|---|
| particuliers | 731 | 136 | 18,6 % |
| notaires | 410 | 20 | 4,9 % |
| plateforme | 875 | 12 | 1,4 % |
| historique | 528 | 10 | 1,9 % |
| agence | 640 | 9 | 1,4 % |

**Avertissements :** 56 prix atypiques, 4 surfaces atypiques, 4 villes incohérentes avec leur région. Ces nombres portent sur tous les biens, quarantaine comprise. Parmi les biens conservés, 53 ont au moins un avertissement.

**Lecture :**
- **Les particuliers concentrent 73 % de la quarantaine**, ce qui confirme la qualité « faible » annoncée. Il s'agit surtout de prix et de surfaces absents.
- **Les notaires, de qualité « très bonne », ont 20 biens en quarantaine.** Ce sont 14 prix absents et les 6 dates `"32/13/2024"`. Une source fiable n'est pas une source sans erreur.
- **Les dates futures** : 5 dates futures avaient été repérées sur la plateforme, mais une seule concerne un bien déclaré vendu. Pour un bien « En vente », une date future n'est pas une impossibilité.
- **15 doublons exacts dans les données brutes, 14 après séparation** : les deux exemplaires d'une des paires sont partis en quarantaine.

## Décisions de conception

**`type_bien` hors référentiel : bloquante.** Le cahier des charges (§6.1) dit « quarantaine si hors référentiel », alors que `regles_metier.md` dit « signaler ». Les deux documents se contredisent, et nous suivons le cahier des charges, qui est le document de référence. Sur les données réelles, la question ne se pose pas : les 3 184 types sont reconnus après normalisation.

**Une ville inconnue du référentiel est signalée comme incohérente.** Sans la ville dans le référentiel, on ne peut pas prouver la cohérence avec la région.

**Seuils d'atypie :** ceux de `regles_metier.md`, sans modification. Ils s'appliquent aux ventes comme aux locations. C'est pourquoi 51 des 56 prix atypiques sont des loyers inférieurs à 100 000 FCFA.

## Les tests

68 tests : les 22 de l'étape 3 (dont certains mis à jour), et 46 nouveaux.

| Fichier | Tests | Ce qu'ils vérifient |
|---|---|---|
| `test_traitement.py` | 17 | conversions (cas paramétrés), `normaliser_selon_referentiel`, `nettoyer_bien` |
| `test_regles.py` | 24 | chaque règle : respectée, violée, non évaluable, cas limites (bornes, Paris, date future) |
| `test_separation.py` | 4 | jeu d'essai (8 propres, HIS-0072 en quarantaine), un seul motif pour `"à négocier"`, AGT-00836 propre après normalisation |
| `test_doublon.py` | 5 | doublon exact, conflit, probable, autre date (probable), location (pas probable) |
| `test_rapport.py` | 6 | compteurs du jeu d'essai, règles sur biens nettoyés, non-évaluables hors du dénominateur, un bien à 2 avertissements compté une fois |
| autres | 12 | étapes 2 et 3 |

Les cas modifiés travaillent sur des **copies** (`.copy()`, `biens + [copie]`). Le jeu d'essai est partagé par tous les fichiers de test : le modifier fait échouer des tests sans rapport avec la modification.

### Les erreurs trouvées pendant l'écriture

- **Des seuils d'atypie inversés** : la condition renvoyait `True` pour les valeurs atypiques.
- **Le jeu d'essai modifié par un test** : sans `.copy()`, un test de doublons a changé le jeu d'essai partagé, et des tests d'autres fichiers ont échoué sans raison apparente.
- **Un champ inventé** (`date_publication` au lieu de `date`) : le test passait, mais ne vérifiait rien, car la date restait la même. Un test doit pouvoir échouer.
- **Des tests qui passent sur du code faux** : le journal était rempli avant le calcul des motifs, donc `en_quarantaine` valait toujours `False`, et les 62 tests passaient quand même. Les tests du rapport ont été écrits pour couvrir ce cas.

## Limites connues

- **La périodicité des locations de l'agence et des particuliers reste vide.** Elle n'est pas devinée, mais aucune règle ne la signale encore.
- **Les trois sortes de manquants ne sont pas encore séparées dans le rapport.** `periodicite` (3 007) mélange les ventes, où elle est sans objet, et les locations sans périodicité. `salles_bain` (410) correspond à une colonne absente chez les notaires.
- **Les villes sont comparées à l'accent près.** `"Thies"` ne serait pas reconnu comme `"Thiès"`.
- **La clé de rapprochement compare les surfaces à l'égalité stricte.** `160.2` et `160.0` ne sont pas rapprochés.
- **Les seuils d'atypie du prix sont les mêmes pour les ventes et les locations.**
- **Rien n'est encore exporté.** Le dossier `sortie/` (données propres, quarantaine, rapport en CSV et JSON) sera produit à l'étape 7.
