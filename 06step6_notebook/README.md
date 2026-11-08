# Étape 6 — Jupyter Notebook

## Objectif

Présenter les distributions, les anomalies, les taux de conformité et les principaux résultats d'analyse dans un notebook.

**Livrable attendu (cahier des charges) :** « notebook documenté, contenant du code exécutable et des conclusions ». Critère de validation (§12) : « le notebook est reproductible ».

## Structure

Le dossier reprend `src/` et `tests/` de l'étape 5 **sans modification**, et ajoute le notebook :

```
06step6_notebook/
├── notebooks/
│   └── 01_exploration.ipynb        # nouveau : 54 cellules (19 de code, 35 de texte)
├── src/                            # identique à l'étape 5
└── tests/                          # identique à l'étape 5 (91 tests)
```

`requirements.txt` (à la racine) ajoute `matplotlib==3.11.2` pour les graphiques et `ipykernel==7.4.0` pour exécuter le notebook avec le venv.

## Exécution

1. Depuis la racine du projet : créer le venv, puis `pip install -r requirements.txt`.
2. Ouvrir `06step6_notebook/notebooks/01_exploration.ipynb` dans VS Code ou Jupyter, et choisir le noyau du **venv**.
3. **Redémarrer le noyau, puis Tout exécuter.**

Toutes les valeurs sont recalculées à partir des fichiers de `sources/`, qui ne sont jamais modifiés. Les tests se lancent toujours depuis `06step6_notebook/`, avec `python -m pytest -v`.

## Le principe : le notebook présente, `src/` calcule

Le notebook **appelle** les fonctions du pipeline (`charger_tout`, `executer_pipeline`) et de l'analyse (`vers_dataframe`, `separer_transactions`, `ajouter_prix_m2`, `resumer`, `statistiques_descriptives`, `resultats_par_groupe`). Il les **affiche** et les **commente**.

- **Un calcul métier n'existe qu'une fois**, dans `src/`, avec ses tests. Le taux de conformité, par exemple, est lu dans le rapport, et non recalculé dans le notebook : deux calculs du même chiffre finissent par diverger.
- **Le notebook ne fait que de la présentation** : construire un `DataFrame`, trier, compter (`value_counts`), tracer un graphique.
- **Aucun chiffre n'est écrit à la main dans le code.** Les valeurs affichées suivent les données. Seules les cellules de lecture citent des chiffres, ceux du tableau juste au-dessus.

### L'import de `src` depuis `notebooks/`

Un notebook s'exécute dans **son propre dossier**. Depuis `notebooks/`, Python ne trouve pas `src/`, d'où un `ModuleNotFoundError`. La première cellule ajoute le dossier de l'étape à `sys.path` :

```python
RACINE = Path.cwd().parent          # notebooks/ → 06step6_notebook/
assert (RACINE / "src").is_dir(), f"src/ introuvable depuis {Path.cwd()}"
sys.path.insert(0, str(RACINE))
```

L'`assert` donne un message clair si le notebook est ouvert depuis un autre dossier.

## Le contenu

Chaque section affiche un tableau ou un graphique, suivi d'une **cellule de lecture** qui dit ce qu'on voit et ce que cela signifie.

| Partie | Sections | Ce qu'on y apprend |
|---|---|---|
| **A. Chargement** | imports, pipeline | 3 184 biens reçus, 2 983 propres, 187 en quarantaine |
| **B. Qualité** | B1 bilan global, B2 quarantaine par source, B3 motifs, B4 taux de conformité par règle, B5 valeurs manquantes | les particuliers concentrent 73 % de la quarantaine ; les notaires, pourtant « très bons », ont le 2ᵉ taux ; 57,6 % de biens entièrement conformes |
| **C. Distributions** | C1 prix de vente, C2 loyers, C3 prix au m² par type, C4 statistiques descriptives | la moyenne dépasse toujours la médiane ; le type de bien est le premier facteur de prix |
| **D. Anomalies** | D1 un exemple par motif de quarantaine, D2 un exemple par avertissement, D3 les 8 doublons probables | des cas réels d'erreur certaine, de valeur atypique et de cas ambigu |
| **E. Ville et région** | E1 par ville, E2 par région (ventes hors terrains) | Dakar et sa périphérie en tête, les autres régions proches les unes des autres |
| **F. Conclusions** | qualité, résultats, décisions et limites, reproduction | |

## Les choix de présentation

**Ventes et locations toujours séparées** (§5.4). Elles ont des graphiques distincts, et le prix au m² n'est calculé que pour les ventes, puisque la périodicité des loyers est inconnue pour l'agence et les particuliers.

**Échelle logarithmique pour les prix de vente (C1) et le prix au m² (C3).** Les prix vont de 5 M à 567 M FCFA. Sur un axe linéaire, la plupart des ventes seraient tassées dans les premières barres. Les intervalles sont créés avec `np.logspace` : avec `bins=40` et un axe log, les barres auraient des largeurs inégales à l'écran. Dans C3, le prix au m² du terrain est environ dix fois plus bas que celui des autres types : sans échelle log, sa boîte serait écrasée contre le bas du graphique.

**Un graphique en barres commence toujours à 0 (B4).** Les taux de conformité vont de 96 % à 100 %. Plutôt que de couper l'axe à 90 %, ce qui exagère les écarts, on trace le **taux de non-conformité** (de 0 à 4 %), dont les longueurs restent proportionnelles.

**Les taux par source plutôt que les nombres (B2).** Les sources n'ont pas la même taille : 12 biens en quarantaine sur 875 ne valent pas 12 sur 410.

**Les manquants séparés en trois sortes (B5).** Le rapport compte 94 % de périodicités manquantes. Mais pour les 2 680 ventes, la périodicité est **sans objet** ; elle **manque vraiment** pour 327 locations sur 504 (65 %). Les manquants de `salles_bain` (410) et de `statut` (528) sont des **colonnes absentes** d'une source entière, les notaires et l'historique.

**Ventes hors terrains pour comparer les villes (E).** La part de terrains varie de 4 % à 34 % selon la ville. Avec les terrains, on compare des mélanges de biens différents, pas des prix : c'est un **effet de composition**. Keur Massar (34 % de terrains) serait la dernière ville au lieu de la 14ᵉ, et Saint-Louis (4 %) la 4ᵉ au lieu de la 22ᵉ.

**Les biens en quarantaine sont montrés bruts (D1)**, tels que la source les a écrits : `'à négocier'`, `'quatre-vingt'`, `32/13/2024`.

## Les principaux résultats

| | Médiane | Moyenne |
|---|---|---|
| Prix de vente | 74,7 M FCFA | 104,6 M FCFA |
| Loyer | 325 000 FCFA | 417 962 FCFA |
| Prix de vente au m² | 624 852 FCFA | 735 795 FCFA |

- **Le type de bien est le premier facteur de prix** : le prix au m² médian va de 64 765 FCFA (terrain) à 906 133 FCFA (villa).
- **Le plateau des prix de vente au-delà de 200 M** (12 % des ventes) est constitué à 95 % de villas.
- **Dakar est la ville la plus chère** hors terrains : 1 147 198 FCFA/m², 63 % au-dessus de la médiane nationale (701 820).
- **Les loyers des trois sources sont du même ordre** (médianes de 315 000 à 345 000 FCFA). Cela suggère que ceux de l'agence et des particuliers sont mensuels, comme ceux de la plateforme. C'est une hypothèse, pas une preuve.
- **Sur les 8 doublons probables**, 2 sont probablement le même bien, 1 est douteux, et 4 ressemblent à des coïncidences. Cela confirme la décision de l'étape 4 : signaler sans fusionner.

## Limites mises en évidence

- **Certaines incohérences ne sont contrôlées par aucune règle.** AGT-01035 est un « studio » de 22 m² avec 5 chambres et 4 salles de bain. Il n'est signalé que pour son prix au m², alors que l'erreur porte probablement sur le type de bien ou la surface.
- **La périodicité des loyers reste inconnue** pour l'agence et les particuliers.
- **Les écarts entre villes sont modérés** (19 à 71 ventes par ville hors terrains). Une différence de quelques dizaines de milliers de FCFA/m² entre deux villes n'est pas significative.
- **Les données sont synthétiques** : les résultats illustrent la démarche, et ne décrivent pas le marché immobilier sénégalais.
- **Rien n'est encore exporté.** Le dossier `sortie/` (données propres, quarantaine, rapport en CSV et JSON) sera produit à l'étape 7.
