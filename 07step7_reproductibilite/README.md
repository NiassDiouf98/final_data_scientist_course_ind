# Étape 7 — Exportation et reproductibilité

## Objectif

Écrire les résultats du pipeline dans des fichiers, et pouvoir tout reproduire avec une seule commande.

**Critères d'acceptation visés :**
- n° 7, **Exports** : `donnees_propres.csv`, `quarantaine.csv`, `rapport_qualite.md` ;
- n° 10, **Reproductibilité** : le pipeline s'exécute de bout en bout avec un seul script.

## Exécution

Depuis la racine du projet, une seule fois :

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Puis, depuis ce dossier :

```bash
cd 07step7_reproductibilite
python -m src.main         # charge, valide, affiche le rapport, écrit les 9 fichiers dans ../sortie/
python -m pytest -v        # 104 tests
```

Le notebook `notebooks/01_exploration.ipynb` se lance comme à l'étape 6 : noyau du venv, puis **Redémarrer le noyau et Tout exécuter**.

## Structure

Le dossier reprend l'étape 6 et ajoute un package `src/export/` :

```
07step7_reproductibilite/
├── notebooks/01_exploration.ipynb   # identique à l'étape 6 (chemins mis à jour)
├── src/
│   ├── constantes.py                # + DOSSIER_SORTIE (sortie/ à la racine du projet)
│   ├── export/                      # nouveau
│   │   ├── ecriture.py              # écrire un CSV, un JSON, un texte
│   │   ├── exportation.py           # quoi écrire : exporter_resultats, exporter_tout
│   │   └── rapport_markdown.py      # le rapport qualité lisible par un humain
│   └── main.py                      # + main(dossier_sortie) : le pipeline de bout en bout
└── tests/
    ├── test_ecriture.py             # nouveau : 5 tests
    ├── test_exportation.py          # nouveau : 4 tests
    └── test_rapport_markdown.py     # nouveau : 4 tests, dont un de bout en bout
```

Les modules ont chacun un rôle :
- **`ecriture.py` sait écrire**, sans rien connaître des biens : il crée le dossier, choisit le séparateur et l'encodage.
- **`exportation.py` sait quoi écrire** : il transforme les résultats du pipeline en lignes (motifs joints, numéro de groupe, colonne `conserve`).
- **`rapport_markdown.py` met en forme** les indicateurs déjà calculés par `rapport.py`. Il ne refait aucun calcul de qualité.

## Les fichiers produits dans `sortie/`

| Fichier | Contenu | Lignes |
|---|---|---|
| `donnees_propres.csv` / `.json` | biens nettoyés, sans quarantaine ni doublon exact | 2 983 |
| `quarantaine.csv` / `.json` | biens **bruts** (tels que la source les a écrits), avec leurs motifs | 187 |
| `avertissements.csv` | un avertissement par ligne : `id_local`, `source`, `raison`, `conserve` | |
| `doublons_probables.csv` | biens rapprochés, avec leur numéro de groupe | 8 groupes |
| `rapport_qualite.json` | tous les indicateurs, pour un traitement automatique | |
| `resume_regles.csv` | une ligne par règle : respectées, violées, non évaluables, évaluables, taux | 14 |
| `rapport_qualite.md` | le rapport qualité lisible par un humain | |

Le rapport [`rapport_qualite.md`](../sortie/rapport_qualite.md) contient :
- la synthèse, avec la définition et le dénominateur de chaque taux ;
- un **profil par source** (critère n° 2) : volumes, quarantaine, avertissements, prix de vente médian, valeurs manquantes ;
- les motifs de quarantaine et les erreurs de conversion par champ ;
- les valeurs manquantes par colonne, en distinguant la périodicité sans objet (ventes) de la périodicité vraiment manquante (327 locations sur 504) ;
- la conformité par règle, avec les évaluables comme dénominateur ;
- les doublons et leur traitement.

## Les choix d'export

**CSV : séparateur `;` et encodage `utf-8-sig`.** Excel en français attend le `;`. La signature UTF-8 (BOM) lui indique l'encodage : sans elle, `Thiès` s'affiche `ThiÃ¨s`. Python relit ces fichiers avec `encoding="utf-8-sig"`.

**JSON : `ensure_ascii=False` et `indent=2`.** Les accents restent lisibles (`Thiès`, pas `Thiès`), et le fichier se lit à l'œil.

**Les motifs de quarantaine sont joints par ` | ` en CSV, et restent une liste en JSON.** Une cellule CSV ne peut contenir qu'un texte. La virgule est exclue : certains motifs en contiennent.

**La quarantaine garde les données brutes.** On doit pouvoir y lire `'à négocier'` ou `32/13/2024`, et non une valeur vide après conversion : c'est ce qui justifie le motif.

**`avertissements.csv` a une colonne `conserve`.** Un bien peut avoir un avertissement et partir en quarantaine pour un autre motif. `conserve = non` le signale.

**`ecrire_csv` refuse une colonne inconnue.** Si une ligne contient une clé absente des colonnes demandées, une `ValueError` est levée, au lieu de perdre la donnée sans prévenir. Une valeur `None` devient une cellule vide.

**Pas de date dans le rapport.** Deux exécutions donnent des fichiers **identiques à l'octet près** (vérifié avec `md5sum`). Git ne montre donc une différence que si les résultats changent. La date de génération est celle du commit.

**`sortie/` est committé.** Un lecteur voit les résultats sans installer le projet, et l'historique git garde la trace de leur évolution.

## La vérification de la reproductibilité

Elle a été faite dans les conditions d'un correcteur, dans un dossier vide :
1. `git clone` du dépôt ;
2. un venv neuf, puis `pip install -r requirements.txt` ;
3. `python -m pytest` : **104 tests passent** ;
4. `python -m src.main` : les 9 fichiers produits sont **identiques** (même `md5sum`) à ceux du dépôt ;
5. le notebook, exécuté de haut en bas dans un noyau neuf : **les 19 cellules de code passent**, sans erreur.

Le test `test_main_de_bout_en_bout` refait les étapes 3 et 4 à chaque lancement des tests. Il exécute `main()` sur les vraies sources dans un dossier temporaire, puis relit les fichiers produits :
- 3 184 biens reçus ;
- 187 lignes en quarantaine, chacune avec au moins un motif (critère n° 4) ;
- propres + quarantaine + doublons exacts = 3 184 : aucun bien n'est perdu.

## Les chiffres à connaître

**91 ou 89 biens avec avertissement ?** La synthèse compte 91 lignes reçues avec avertissement. Le tableau par source en compte 89, car il porte sur les biens uniques : PLT-00692 et PLT-00801 ont un avertissement **et** sont des doublons exacts. Le rapport l'explique sous le tableau.

**193 motifs pour 187 biens.** Un bien peut cumuler plusieurs motifs, par exemple un prix et une surface manquants.

## Limites

- **Les prix s'écrivent parfois avec `.0`** dans `donnees_propres.csv` (`60581000.0` à côté de `57620000`). Le prix converti est un `float` quand la source écrivait un décimal, un `int` sinon. La valeur est la même, et un tableur ou Pandas les lit comme des nombres.
- **Pas d'export Excel (`.xlsx`).** Les CSV s'ouvrent dans Excel ; un `.xlsx` serait un plus, pas une obligation du cahier des charges.
- **`sortie/` est écrasé à chaque exécution.** C'est voulu : il reflète toujours le code et les sources du moment. Les versions précédentes restent dans git.
