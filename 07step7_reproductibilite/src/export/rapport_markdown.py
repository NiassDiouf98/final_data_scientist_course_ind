"""Le rapport qualité en Markdown, lisible par un humain (critère d'acceptation n° 7).

Pas de date de génération : le fichier est identique d'une exécution à l'autre,
et git ne montre une différence que si les résultats changent.
"""
from collections import Counter
from statistics import median

from src.constantes import CHAMPS_ATTENDUS, VALEURS_VIDES


def _nombre(valeur):
    """3184 -> « 3 184 »."""
    return f"{valeur:,}".replace(",", " ")


def _pourcentage(partie, total):
    """(187, 3184) -> « 5,9 % » ; « — » si le total est nul."""
    if not total:
        return "—"
    return f"{partie / total * 100:.1f} %".replace(".", ",")


def _tableau(entetes, lignes):
    """Un tableau Markdown à partir d'une liste d'entêtes et d'une liste de lignes."""
    texte = ["| " + " | ".join(entetes) + " |", "|" + "---|" * len(entetes)]
    texte += ["| " + " | ".join(str(cellule) for cellule in ligne) + " |" for ligne in lignes]
    return "\n".join(texte)


def _section_synthese(resultats):
    r = resultats["rapport"]
    total = r["total_recus"]
    conformes = r["entierement_conformes"]
    lignes = [
        ("Biens reçus", _nombre(total), ""),
        ("Mis en quarantaine", _nombre(r["quarantaine"]), _pourcentage(r["quarantaine"], total)),
        ("Conservés avec avertissement", _nombre(r["avec_avertissement"]),
         _pourcentage(r["avec_avertissement"], total)),
        ("Corrigés (normalisation fiable)", _nombre(r["corriges"]), _pourcentage(r["corriges"], total)),
        ("Entièrement conformes", _nombre(conformes["nombre"]), _pourcentage(conformes["nombre"], total)),
        ("Doublons exacts retirés", _nombre(r["doublons_exacts"]["nombre"]),
         _pourcentage(r["doublons_exacts"]["nombre"], total)),
        ("Biens propres et uniques", _nombre(len(resultats["propres"])),
         _pourcentage(len(resultats["propres"]), total)),
    ]
    return "\n\n".join([
        "## Synthèse",
        _tableau(["Indicateur", "Nombre", "% des reçus"], lignes),
        f"- **Entièrement conforme** : {conformes['definition']}. "
        f"Dénominateur : {conformes['denominateur']}.",
        f"- **Taux de doublons exacts** : {r['doublons_exacts']['definition_taux']}.",
        "- Un bien n'est compté qu'une fois dans chaque ligne, même s'il a plusieurs motifs ou avertissements.",
    ])


def _section_sources(biens, resultats):
    """Profil par source : volumes, quarantaine, avertissements, prix médian, valeurs manquantes."""
    recus = Counter(b["source"] for b in biens)
    quarantaine = Counter(q["bien"]["source"] for q in resultats["quarantaine"])
    propres = Counter(b["source"] for b in resultats["propres"])
    ids_conserves = {b["id_local"] for b in resultats["propres"]}
    source_de = {b["id_local"]: b["source"] for b in resultats["propres"]}
    avec_avertissement = Counter(
        source_de[i] for i in {i for i, _ in resultats["avertissements"] if i in ids_conserves}
    )

    lignes = []
    for source in sorted(recus, key=lambda s: quarantaine[s] / recus[s], reverse=True):
        prix_ventes = [b["prix"] for b in resultats["propres"]
                       if b["source"] == source and b["type_transaction"] == "vente"]
        prix_median = f"{median(prix_ventes) / 1e6:.1f} M".replace(".", ",") if prix_ventes else "—"
        lignes.append((
            source, _nombre(recus[source]), _nombre(quarantaine[source]),
            _pourcentage(quarantaine[source], recus[source]), _nombre(propres[source]),
            _nombre(avec_avertissement[source]), prix_median,
        ))

    # Valeurs manquantes par source, sur les biens BRUTS, pour les colonnes concernées
    manquants = {s: Counter() for s in recus}
    for bien in biens:
        for champ in CHAMPS_ATTENDUS:
            if bien[champ] in VALEURS_VIDES:
                manquants[bien["source"]][champ] += 1
    colonnes = [c for c in CHAMPS_ATTENDUS if any(manquants[s][c] for s in recus)]
    lignes_manquants = [
        [source] + [_nombre(manquants[source][c]) if manquants[source][c] else "" for c in colonnes]
        for source in sorted(recus)
    ]

    return "\n\n".join([
        "## Par source",
        _tableau(["Source", "Reçus", "Quarantaine", "Taux", "Propres uniques",
                  "Conservés avec avertissement", "Prix de vente médian"], lignes),
        "« Propres uniques », « Conservés avec avertissement » et le prix médian portent sur les biens "
        "**après retrait des doublons exacts**. La synthèse compte, elle, les lignes reçues : un bien "
        "avec avertissement reçu en double y compte deux fois.",
        "### Valeurs manquantes par source (biens bruts)",
        _tableau(["Source"] + colonnes, lignes_manquants),
        "Une cellule vide signifie aucune valeur manquante. Une colonne entièrement vide pour une source "
        "(par exemple `salles_bain` chez les notaires) est une **colonne absente** de cette source, "
        "pas une valeur oubliée.",
    ])


def _section_manquants(biens, resultats):
    r = resultats["rapport"]
    total = r["total_recus"]
    lignes = [
        (f"`{champ}`", _nombre(n), _pourcentage(n, total))
        for champ, n in sorted(r["manquants_par_colonne"].items(), key=lambda e: -e[1])
    ]
    locations = [b for b in biens if b["type_transaction"] == "location"]
    sans_periodicite = sum(b["periodicite"] in VALEURS_VIDES for b in locations)
    return "\n\n".join([
        "## Valeurs manquantes par colonne",
        _tableau(["Colonne", "Manquantes", "% des reçus"], lignes),
        f"**`periodicite`** n'a de sens que pour une location : pour une vente, elle est sans objet. "
        f"Elle manque vraiment pour {_nombre(sans_periodicite)} locations sur {_nombre(len(locations))} "
        f"({_pourcentage(sans_periodicite, len(locations))}).",
    ])


def _section_quarantaine(resultats):
    r = resultats["rapport"]
    motifs = Counter(m for q in resultats["quarantaine"] for m in q["motifs"])
    erreurs = sorted(r["erreurs_conversion_par_champ"].items(), key=lambda e: -e[1])
    return "\n\n".join([
        "## Quarantaine",
        f"{_nombre(r['quarantaine'])} biens, gardés **bruts** (tels que la source les a écrits) "
        "dans `quarantaine.csv` et `quarantaine.json`, avec leurs motifs.",
        "### Motifs",
        _tableau(["Motif", "Biens"], [(m, _nombre(n)) for m, n in motifs.most_common()]),
        f"Total des motifs : {_nombre(sum(motifs.values()))} pour {_nombre(r['quarantaine'])} biens "
        "(un bien peut cumuler plusieurs motifs).",
        "### Erreurs de conversion par champ",
        _tableau(["Champ", "Erreurs"], [(f"`{c}`", _nombre(n)) for c, n in erreurs]),
        "Une erreur de conversion est une valeur présente mais illisible (`'à négocier'`, `'32/13/2024'`). "
        "Une valeur vide est comptée dans les valeurs manquantes.",
    ])


def _section_regles(resultats):
    regles = resultats["rapport"]["regles"]
    total = resultats["rapport"]["total_recus"]
    lignes = []
    for nom, c in sorted(regles.items(), key=lambda e: (e[1]["taux_conformite"] is None,
                                                        e[1]["taux_conformite"] or 0)):
        taux = "—" if c["taux_conformite"] is None else f"{c['taux_conformite']:.1f} %".replace(".", ",")
        lignes.append((f"`{nom}`", _nombre(c["respectee"]), _nombre(c["violee"]),
                       _nombre(c["non_evaluable"]), _nombre(c["evaluables"]), taux))
    return "\n\n".join([
        "## Conformité par règle",
        "Taux de conformité = respectées / **évaluables** × 100, avec évaluables = respectées + violées. "
        "Les non-évaluables (valeur absente, ou règle qui ne concerne pas le bien) sont comptés à part, "
        f"et jamais comme conformes. Les règles sont évaluées sur les {_nombre(total)} biens reçus, "
        "quarantaine comprise.",
        _tableau(["Règle", "Respectées", "Violées", "Non évaluables", "Évaluables (dénominateur)", "Taux"],
                 lignes),
    ])


def _section_doublons(resultats):
    r = resultats["rapport"]
    return "\n\n".join([
        "## Doublons",
        _tableau(["Cas", "Nombre", "Traitement"], [
            ("Doublons exacts (même source, même identifiant, mêmes valeurs)",
             _nombre(r["doublons_exacts"]["nombre"]), "un exemplaire gardé"),
            ("Conflits (même source, même identifiant, valeurs différentes)",
             _nombre(r["conflits"]), "quarantaine"),
            ("Doublons probables (même type, ville, surface et transaction)",
             _nombre(r["doublons_probables"]), "gardés et signalés, jamais fusionnés"),
        ]),
        "Le détail des doublons probables est dans `doublons_probables.csv`.",
    ])


FICHIERS = """## Fichiers produits

| Fichier | Contenu |
|---|---|
| `donnees_propres.csv` / `.json` | biens nettoyés, sans quarantaine ni doublon exact |
| `quarantaine.csv` / `.json` | biens bruts et leurs motifs (séparés par ` \\| ` en CSV, en liste en JSON) |
| `avertissements.csv` | un avertissement par ligne ; `conserve = non` si le bien est en quarantaine pour un autre motif |
| `doublons_probables.csv` | biens rapprochés, avec leur numéro de groupe |
| `rapport_qualite.json` | tous les indicateurs, pour un traitement automatique |
| `resume_regles.csv` | une ligne par règle |

Les CSV utilisent le séparateur `;` et l'encodage UTF-8 avec signature (lisible par Excel)."""


def produire_rapport_markdown(biens, resultats):
    """Renvoie le rapport qualité complet, en Markdown, à partir des biens reçus et des résultats."""
    sections = [
        "# Rapport de qualité — ImmoAnalyse",
        "Généré par `python -m src.main` à partir des fichiers de `sources/`. "
        "Données synthétiques : elles ne décrivent pas le marché réel.",
        _section_synthese(resultats),
        _section_sources(biens, resultats),
        _section_quarantaine(resultats),
        _section_manquants(biens, resultats),
        _section_regles(resultats),
        _section_doublons(resultats),
        FICHIERS,
    ]
    return "\n\n".join(sections) + "\n"
