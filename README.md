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
cd 06step6_notebook
python -m src.main         # pipeline complet : nettoyage, validation, quarantaine, doublons, rapport qualité
python -m pytest -v        # tests de l'étape
```

Le notebook d'analyse est `06step6_notebook/notebooks/01_exploration.ipynb`. Ouvre-le avec le noyau du venv, puis Redémarrer le noyau et Tout exécuter.

Pour l'étape 1 : `python3 01step1_python_data_structure/main.py` depuis la racine.

`pytest` lancé depuis la racine ne fonctionne plus : les étapes 2 à 6 ont chacune un package `tests` avec des fichiers du même nom, et pytest refuse de les mélanger (`import file mismatch`).

## Avancement

| Étape | Sujet | État |
|---|---|---|
| 1 | Python et structures de données | ✅ Terminée — voir [01step1_python_data_structure/README.md](01step1_python_data_structure/README.md) |
| 2 | Programmation modulaire et POO | ✅ Terminée — voir [02step2_POO/README.md](02step2_POO/README.md) |
| 3 | Chargement des données | ✅ Terminée — voir [03step3_chargement/README.md](03step3_chargement/README.md) |
| 4 | Validation et nettoyage | ✅ Terminée — voir [04step4_validation/README.md](04step4_validation/README.md) |
| 5 | NumPy et Pandas | ✅ Terminée — voir [05step5_analyse/README.md](05step5_analyse/README.md) |
| 6 | Jupyter Notebook | ✅ Terminée — voir [06step6_notebook/README.md](06step6_notebook/README.md) |
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
├── 05step5_analyse/                # étape 5 : statistiques NumPy/Pandas, prix au m², seuils du §6.2
├── 06step6_notebook/               # étape 6 : notebook d'analyse exploratoire (notebooks/01_exploration.ipynb)
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

## Résultats de la validation (étapes 4 et 5)

| Indicateur | Valeur |
|---|---|
| Biens reçus | 3 184 |
| Mis en quarantaine | 187 (5,9 %), dont 136 chez les particuliers |
| Conservés avec avertissement | 91 (53 à l'étape 4, avant les seuils du §6.2) |
| Corrigés (normalisation) | 1 216 |
| Entièrement conformes | 1 834 (57,6 %) : ni quarantaine, ni avertissement, ni correction |
| Doublons exacts / conflits / doublons probables | 14 / 0 / 8 |
| Biens propres et uniques | 2 983 (2 534 ventes, 449 locations) |

Le détail est dans les README de l'[étape 4](04step4_validation/README.md) et de l'[étape 5](05step5_analyse/README.md).

## Résultats d'analyse (étapes 5 et 6)

Ventes et locations sont toujours analysées séparément.

| | Médiane | Moyenne |
|---|---|---|
| Prix de vente | 74,7 M FCFA | 104,6 M FCFA |
| Loyer | 325 000 FCFA | 417 962 FCFA |
| Prix de vente au m² | 624 852 FCFA | 735 795 FCFA |

La moyenne est au-dessus de la médiane : quelques biens très chers étirent la distribution vers la droite.

- **Le type de bien est le premier facteur de prix** : le prix au m² médian va de 64 765 FCFA (terrain) à 906 133 FCFA (villa).
- **Dakar est la ville la plus chère** : 1 147 198 FCFA/m² hors terrains, 63 % au-dessus de la médiane nationale. Sa périphérie suit (Pikine, Rufisque, Guédiawaye). Les autres régions sont proches les unes des autres.
- **Les loyers des trois sources sont du même ordre** (médianes de 315 000 à 345 000 FCFA). Cela suggère des loyers mensuels partout, mais ce n'est qu'une hypothèse.

Le détail, avec les graphiques et leurs lectures, est dans le [notebook](06step6_notebook/notebooks/01_exploration.ipynb) et le [README de l'étape 6](06step6_notebook/README.md).

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

**Ventes et locations ne sont jamais mélangées** (§5.4). Le prix au m² n'est calculé que pour les ventes : la périodicité des loyers est inconnue pour l'agence et les particuliers.

**Chaque seuil d'atypie ne juge que les biens concernés.** `prix_atypique` ne s'applique plus qu'aux ventes, `loyer_atypique` (25 000 à 5 000 000 FCFA) aux locations. Un bien non concerné est « non évaluable », et non « respecté » : le taux de conformité ne compte que les biens concernés.

**Locaux commerciaux et terrains exclus du contrôle salles de bain / chambres.** Ce ne sont pas des logements : 0 chambre y est normal.

**Prix au m² : fourchette large.** Elle est déduite des cas extrêmes du référentiel des catégories (`prix_min / surface_max` à `prix_max / surface_min`). Peu de faux avertissements, mais elle ne détecte que les incohérences grossières (×211 entre les bornes pour le terrain).

**Comparaison des villes : ventes hors terrains.** La part de terrains varie de 4 % à 34 % selon la ville, et un terrain vaut environ dix fois moins au m². Avec les terrains, on comparerait des mélanges de biens différents (effet de composition) : Keur Massar serait la ville la moins chère, au lieu de la 14ᵉ.

**Notebook : le notebook présente, `src/` calcule.** Aucun calcul métier n'est refait dans le notebook : il appelle les fonctions testées du pipeline et de l'analyse, puis affiche et commente leurs résultats.

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
