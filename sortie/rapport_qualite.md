# Rapport de qualité — ImmoAnalyse

Généré par `python -m src.main` à partir des fichiers de `sources/`. Données synthétiques : elles ne décrivent pas le marché réel.

## Synthèse

| Indicateur | Nombre | % des reçus |
|---|---|---|
| Biens reçus | 3 184 |  |
| Mis en quarantaine | 187 | 5,9 % |
| Conservés avec avertissement | 91 | 2,9 % |
| Corrigés (normalisation fiable) | 1 216 | 38,2 % |
| Entièrement conformes | 1 834 | 57,6 % |
| Doublons exacts retirés | 14 | 0,4 % |
| Biens propres et uniques | 2 983 | 93,7 % |

- **Entièrement conforme** : ni quarantaine, ni avertissement, ni correction. Dénominateur : nombre total de biens reçus.

- **Taux de doublons exacts** : lignes en trop / nombre total de biens reçus × 100.

- Un bien n'est compté qu'une fois dans chaque ligne, même s'il a plusieurs motifs ou avertissements.

## Par source

| Source | Reçus | Quarantaine | Taux | Propres uniques | Conservés avec avertissement | Prix de vente médian |
|---|---|---|---|---|---|---|
| particuliers | 731 | 136 | 18,6 % | 595 | 25 | 62,0 M |
| notaires | 410 | 20 | 4,9 % | 390 | 2 | 80,9 M |
| historique | 528 | 10 | 1,9 % | 518 | 19 | 67,6 M |
| agence | 640 | 9 | 1,4 % | 631 | 19 | 80,5 M |
| plateforme | 875 | 12 | 1,4 % | 849 | 24 | 79,5 M |

« Propres uniques », « Conservés avec avertissement » et le prix médian portent sur les biens **après retrait des doublons exacts**. La synthèse compte, elle, les lignes reçues : un bien avec avertissement reçu en double y compte deux fois.

### Valeurs manquantes par source (biens bruts)

| Source | ville | prix | surface | salles_bain | periodicite | statut |
|---|---|---|---|---|---|---|
| agence |  |  |  |  | 640 |  |
| historique | 8 | 10 |  |  | 528 | 528 |
| notaires |  | 14 |  | 410 | 410 |  |
| particuliers |  | 61 | 75 |  | 731 |  |
| plateforme |  |  | 5 |  | 698 |  |

Une cellule vide signifie aucune valeur manquante. Une colonne entièrement vide pour une source (par exemple `salles_bain` chez les notaires) est une **colonne absente** de cette source, pas une valeur oubliée.

## Quarantaine

187 biens, gardés **bruts** (tels que la source les a écrits) dans `quarantaine.csv` et `quarantaine.json`, avec leurs motifs.

### Motifs

| Motif | Biens |
|---|---|
| Le prix doit être présent et supérieur à zéro | 90 |
| La surface doit être présente et supérieure à zéro | 84 |
| prix illisible : 'à négocier' | 6 |
| date illisible : '32/13/2024' | 6 |
| surface illisible : 'quatre-vingt' | 4 |
| prix illisible : 'None FCFA' | 2 |
| La date d'un bien vendu ne peut pas être dans le futur | 1 |

Total des motifs : 193 pour 187 biens (un bien peut cumuler plusieurs motifs).

### Erreurs de conversion par champ

| Champ | Erreurs |
|---|---|
| `prix` | 8 |
| `date` | 6 |
| `surface` | 4 |

Une erreur de conversion est une valeur présente mais illisible (`'à négocier'`, `'32/13/2024'`). Une valeur vide est comptée dans les valeurs manquantes.

## Valeurs manquantes par colonne

| Colonne | Manquantes | % des reçus |
|---|---|---|
| `periodicite` | 3 007 | 94,4 % |
| `statut` | 528 | 16,6 % |
| `salles_bain` | 410 | 12,9 % |
| `prix` | 85 | 2,7 % |
| `surface` | 80 | 2,5 % |
| `ville` | 8 | 0,3 % |

**`periodicite`** n'a de sens que pour une location : pour une vente, elle est sans objet. Elle manque vraiment pour 327 locations sur 504 (64,9 %).

## Conformité par règle

Taux de conformité = respectées / **évaluables** × 100, avec évaluables = respectées + violées. Les non-évaluables (valeur absente, ou règle qui ne concerne pas le bien) sont comptés à part, et jamais comme conformes. Les règles sont évaluées sur les 3 184 biens reçus, quarantaine comprise.

| Règle | Respectées | Violées | Non évaluables | Évaluables (dénominateur) | Taux |
|---|---|---|---|---|---|
| `salles_bain_atypiques` | 2 095 | 88 | 1 001 | 2 183 | 96,0 % |
| `prix_positif` | 3 086 | 98 | 0 | 3 184 | 96,9 % |
| `surface_positive` | 3 096 | 88 | 0 | 3 184 | 97,2 % |
| `loyer_atypique` | 478 | 2 | 2 704 | 480 | 99,6 % |
| `prix_m2_hors_fourchette` | 2 547 | 7 | 630 | 2 554 | 99,7 % |
| `date_valide` | 3 178 | 6 | 0 | 3 184 | 99,8 % |
| `prix_atypique` | 2 608 | 3 | 573 | 2 611 | 99,9 % |
| `surface_atypique` | 3 096 | 4 | 84 | 3 100 | 99,9 % |
| `ville_region_coherentes` | 3 172 | 4 | 8 | 3 176 | 99,9 % |
| `type_bien_reconnu` | 3 184 | 0 | 0 | 3 184 | 100,0 % |
| `transaction_valide` | 3 184 | 0 | 0 | 3 184 | 100,0 % |
| `id_present` | 3 184 | 0 | 0 | 3 184 | 100,0 % |
| `date_non_future_si_vendu` | 3 177 | 1 | 6 | 3 178 | 100,0 % |
| `chambres_atypiques` | 1 134 | 0 | 2 050 | 1 134 | 100,0 % |

## Doublons

| Cas | Nombre | Traitement |
|---|---|---|
| Doublons exacts (même source, même identifiant, mêmes valeurs) | 14 | un exemplaire gardé |
| Conflits (même source, même identifiant, valeurs différentes) | 0 | quarantaine |
| Doublons probables (même type, ville, surface et transaction) | 8 | gardés et signalés, jamais fusionnés |

Le détail des doublons probables est dans `doublons_probables.csv`.

## Fichiers produits

| Fichier | Contenu |
|---|---|
| `donnees_propres.csv` / `.json` | biens nettoyés, sans quarantaine ni doublon exact |
| `quarantaine.csv` / `.json` | biens bruts et leurs motifs (séparés par ` \| ` en CSV, en liste en JSON) |
| `avertissements.csv` | un avertissement par ligne ; `conserve = non` si le bien est en quarantaine pour un autre motif |
| `doublons_probables.csv` | biens rapprochés, avec leur numéro de groupe |
| `rapport_qualite.json` | tous les indicateurs, pour un traitement automatique |
| `resume_regles.csv` | une ligne par règle |

Les CSV utilisent le séparateur `;` et l'encodage UTF-8 avec signature (lisible par Excel).
