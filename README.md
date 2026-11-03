# ImmoAnalyse

Pipeline Python qui transforme des données immobilières brutes et hétérogènes (CSV, Excel, JSON) en données contrôlées, accompagnées d'un rapport de qualité chiffré.

Projet fil rouge du Module 1 « Python pour l'IA et le Machine Learning ». Le détail des attentes est dans `CAHIER DES CHARGES — IMMOANALYSE.pdf`.

## Installation

Prérequis : Python 3.12 ou plus récent.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Exécution

Avec l'environnement virtuel activé, les tests se lancent **depuis le dossier de chaque étape** :

```bash
cd 04step4_validation
python -m src.main         # pipeline complet : nettoyage, validation, quarantaine, doublons, rapport qualité
python -m pytest -v        # tests de l'étape
```

Pour l'étape 1 : `python3 01step1_python_data_structure/main.py` depuis la racine.

`pytest` lancé depuis la racine ne fonctionne plus : les étapes 2 à 4 ont chacune un package `tests` avec des fichiers du même nom, et pytest refuse de les mélanger (`import file mismatch`).

## Avancement

| Étape | Sujet | État |
|---|---|---|
| 1 | Python et structures de données | ✅ Terminée — voir [01step1_python_data_structure/README.md](01step1_python_data_structure/README.md) |
| 2 | Programmation modulaire et POO | ✅ Terminée — voir [02step2_POO/README.md](02step2_POO/README.md) |
| 3 | Chargement des données | ✅ Terminée — voir [03step3_chargement/README.md](03step3_chargement/README.md) |
| 4 | Validation et nettoyage | ✅ Terminée — voir [04step4_validation/README.md](04step4_validation/README.md) |
| 5 | NumPy et Pandas | À faire |
| 6 | Jupyter Notebook | À faire |
| 7 | Exportation et reproductibilité | À faire |

## Structure du projet

```
immoanalyse_dataset/
├── sources/                      # 5 flux bruts — ne jamais modifier
├── referentiels/                 # géographie, catégories, dictionnaire, règles métier
├── 01step1_python_data_structure/  # étape 1 : fonctions de base et tests
├── 02step2_POO/                    # étape 2 : modules (src/), classe RegleValidation, tests/
├── 03step3_chargement/             # étape 3 : lecture et harmonisation des 5 sources, inventaire
├── 04step4_validation/             # étape 4 : nettoyage, règles, quarantaine, doublons, rapport qualité
├── requirements.txt
└── README.md
```

## Les sources

| Source | Format | Lignes | Qualité annoncée |
|---|---|---|---|
| `plateforme_immo_sn.csv` | CSV `;` | 875 | Moyenne (prix parfois en millions) |
| `agence_teranga.xlsx` | Excel, 2 feuilles | 640 | Bonne |
| `particuliers.json` | JSON imbriqué | 731 | Faible |
| `notaires.csv` | CSV `,` | 410 | Très bonne |
| `import_historique.csv` | CSV `;`, latin-1 | 528 | Mauvaise |

## Format commun

Après chargement, chaque bien, quelle que soit sa source, est représenté avec ces 13 champs :

| Champ | Type attendu | Remarque |
|---|---|---|
| `source` | texte | Provenance de l'enregistrement |
| `id_local` | texte | Identifiant d'origine, conservé tel quel (non universel) |
| `date` | date | Date de l'annonce ou de l'acte |
| `type_transaction` | `vente` / `location` | Déterminé **avant** tout traitement des prix |
| `type_bien` | une des 7 catégories | Appartement, Studio, Chambre, Villa, Maison, Terrain, Local commercial |
| `region` | texte | |
| `ville` | texte | |
| `prix` | nombre (FCFA) | Prix **demandé** pour une vente (pas forcément le prix conclu), loyer pour une location |
| `periodicite` | mensuel, trimestriel, semestriel, annuel | Locations uniquement |
| `surface` | nombre (m²) | |
| `chambres` | entier | |
| `salles_bain` | entier | Vide si la source ne le fournit pas |
| `statut` | texte | |

Le chargement ne fait que renommer et ranger les colonnes. Toute correction a lieu à l'étape de validation et de nettoyage.

## Résultats de la validation (étape 4)

| Indicateur | Valeur |
|---|---|
| Biens reçus | 3 184 |
| Mis en quarantaine | 187 (5,9 %), dont 136 chez les particuliers |
| Conservés avec avertissement | 53 |
| Corrigés (normalisation) | 1 216 |
| Entièrement conformes | 1 839 (57,8 %) : ni quarantaine, ni avertissement, ni correction |
| Doublons exacts / conflits / doublons probables | 14 / 0 / 8 |

Le détail est dans le [README de l'étape 4](04step4_validation/README.md).

### Correspondance des colonnes

| Champ commun | Plateforme | Agence | Particuliers | Notaires | Historique |
|---|---|---|---|---|---|
| id_local | ref_plateforme | Code | id | id_acte | ID |
| date | date_mise_en_ligne | Date | date | date_acte | DateVente |
| type_transaction | type_transaction | *(déduit)* | details.transaction | *(déduit)* | *(déduit)* |
| type_bien | categorie | Type | details.type | type_bien | TypeBien |
| region | region | Region | localisation.region | region | Region |
| ville | commune | Ville | localisation.ville | ville | Ville |
| prix | prix (+ devise) | Prix_FCFA | details.prix | montant_fcfa | Prix |
| surface | surface | Surface_m2 | details.surface | superficie | Surface |
| chambres | pieces | Chambres | details.chambres | nb_chambres | Chambres |
| salles_bain | sdb | SDB | details.sdb | *(absent)* | SallesBain |
| statut | statut | Statut | statut | statut | *(absent)* |

## Décisions de conception

Chaque décision s'appuie sur une observation des données.

**Agence : le statut « Disponible » correspond à une location.**
Les 59 biens « Disponible » ont tous un prix inférieur à 5 M FCFA (médiane : 285 000), comme les biens « Loué » (médiane : 460 000). Les biens « Vendu » et « En vente » ont tous un prix supérieur à 5 M FCFA (médianes : 77,9 M et 84,3 M). La périodicité de ces loyers est inconnue : elle reste vide et sera signalée, sans être devinée.

**Historique : tous les biens sont des ventes.**
Aucun des 528 prix n'est inférieur à 5 M FCFA (médiane : 67,6 M), et la date s'appelle `DateVente`.

**Notaires : tous les biens sont des ventes.**
Les statuts sont « Vendu », « Vente conclue » et « Acte signé ».

**Plateforme : le nombre de pièces est traité comme un nombre de chambres.**
Les terrains et locaux commerciaux ont toujours 0 pièce, et les valeurs (0 à 6) ont la même échelle que les chambres des autres sources. C'est une **hypothèse** : une pièce n'est pas forcément une chambre.

**Plateforme : la devise donne la périodicité.**
La devise vaut `FCFA` pour les 698 ventes et `FCFA/mois` pour les 177 locations. `FCFA/mois` est traduit en `periodicite = "mensuel"`. C'est la seule source où la périodicité est connue.

**Particuliers : la périodicité des locations est inconnue.**
Les 219 locations n'indiquent pas de périodicité. Comme pour l'agence, elle reste vide et sera signalée, sans être devinée.

**Validation : normaliser d'abord, valider ensuite.**
Une date `24/07/2022` ou un prix `26 620 000` sont normalisables (`regles_metier.md`). Ils sont corrigés avant que les règles ne s'appliquent. Seul ce qui reste illisible ou impossible part en quarantaine, avec la donnée **brute** et un motif.

**`type_bien` hors référentiel : quarantaine.**
Le cahier des charges (§6.1) et `regles_metier.md` se contredisent : le premier dit « quarantaine », le second « signaler ». Nous suivons le cahier des charges. Sur les données réelles, les 3 184 types sont reconnus après normalisation.

**Doublons : la date ne fait pas partie de la clé de rapprochement.**
La clé est `(type_bien, ville, surface, type_transaction)`. La date d'un acte notarié et la date de mise en ligne d'une annonce sont différentes par nature. Les doublons probables sont signalés, jamais fusionnés.

**Conflits d'identifiant : quarantaine.**
Deux lignes de la même source avec le même identifiant, mais des valeurs différentes : on ne sait pas laquelle est juste. Il n'y en a aucune dans les données actuelles.

**Agence : seule la feuille « Annonces » contient des biens.**
La feuille « Params » contient des métadonnées (version, date d'export). Elle n'est pas chargée comme données.

## Données et consignes du pack

### Nature
Données **synthétiques** inspirées du contexte immobilier sénégalais. Aucune transaction réelle. Elles ne doivent pas servir à estimer les prix du marché.

### Fichiers fournis
- `sources/` : 5 flux bruts hétérogènes (CSV, Excel, JSON).
- `referentiels/` : géographie, catégories, dictionnaire, règles métier.
- `formateur/` : corrigé confidentiel — **ne pas distribuer aux étudiants**.

### Consignes
1. Ne pas modifier les fichiers de `sources/`.
2. Produire un dossier `sortie/` avec données propres, quarantaine et rapport qualité.
3. Justifier chaque décision de nettoyage.
4. Distinguer erreur certaine, valeur atypique et cas ambigu.
