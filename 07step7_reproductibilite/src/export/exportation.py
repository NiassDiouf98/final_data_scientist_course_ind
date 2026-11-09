from src.constantes import CHAMPS_ATTENDUS
from src.export.ecriture import ecrire_csv, ecrire_json, ecrire_texte
from src.export.rapport_markdown import produire_rapport_markdown

SEPARATEUR_MOTIFS = " | "      # pas de virgule : certains motifs en contiennent déjà


def _lignes_quarantaine(quarantaine):
    """Une ligne par bien : les 13 champs BRUTS, plus les motifs joints en une cellule."""
    return [
        {**q["bien"], "motifs": SEPARATEUR_MOTIFS.join(q["motifs"])}
        for q in quarantaine
    ]


def _lignes_avertissements(resultats):
    """Une ligne par avertissement : identifiant, source, raison, et si le bien est conservé.

    La liste du pipeline contient aussi les avertissements des biens partis en quarantaine
    pour un autre motif : la colonne « conserve » permet de les distinguer.
    """
    sources = {q["bien"]["id_local"]: q["bien"]["source"] for q in resultats["quarantaine"]}
    sources.update({b["id_local"]: b["source"] for b in resultats["propres"]})
    ids_conserves = {b["id_local"] for b in resultats["propres"]}
    return [
        {
            "id_local": id_local,
            "source": sources.get(id_local),
            "raison": raison,
            "conserve": "oui" if id_local in ids_conserves else "non",
        }
        for id_local, raison in resultats["avertissements"]
    ]


def _lignes_doublons_probables(doublons_probables):
    """Une ligne par bien, avec le numéro de son groupe (les biens d'un groupe se suivent)."""
    return [
        {"groupe": numero, **bien}
        for numero, groupe in enumerate(doublons_probables, start=1)
        for bien in groupe
    ]


def _lignes_resume_regles(rapport):
    """Une ligne par règle, avec le dénominateur du taux (les évaluables)."""
    return [
        {"regle": nom, **compteurs}
        for nom, compteurs in rapport["regles"].items()
    ]


def exporter_resultats(resultats, dossier):
    """Écrit les résultats de executer_pipeline dans dossier.

    Renvoie {nom du fichier: chemin}. Les fichiers existants sont remplacés.
    """
    rapport = resultats["rapport"]
    quarantaine = _lignes_quarantaine(resultats["quarantaine"])
    colonnes_regles = ["regle", "respectee", "violee", "non_evaluable", "evaluables", "taux_conformite"]

    fichiers = [
        ecrire_csv(resultats["propres"], dossier / "donnees_propres.csv", CHAMPS_ATTENDUS),
        ecrire_json(resultats["propres"], dossier / "donnees_propres.json"),
        ecrire_csv(quarantaine, dossier / "quarantaine.csv", CHAMPS_ATTENDUS + ["motifs"]),
        # En JSON, les motifs restent une liste
        ecrire_json(resultats["quarantaine"], dossier / "quarantaine.json"),
        ecrire_csv(_lignes_avertissements(resultats), dossier / "avertissements.csv",
                   ["id_local", "source", "raison", "conserve"]),
        ecrire_csv(_lignes_doublons_probables(resultats["doublons_probables"]),
                   dossier / "doublons_probables.csv", ["groupe"] + CHAMPS_ATTENDUS),
        ecrire_json(rapport, dossier / "rapport_qualite.json"),
        ecrire_csv(_lignes_resume_regles(rapport), dossier / "resume_regles.csv", colonnes_regles),
    ]
    return {chemin.name: chemin for chemin in fichiers}


def exporter_tout(biens, resultats, dossier):
    """Écrit les fichiers de données (exporter_resultats) et le rapport rapport_qualite.md.

    biens : les biens reçus, bruts (pour le profil par source du rapport).
    Renvoie {nom du fichier: chemin}.
    """
    fichiers = exporter_resultats(resultats, dossier)
    rapport_md = ecrire_texte(produire_rapport_markdown(biens, resultats), dossier / "rapport_qualite.md")
    fichiers[rapport_md.name] = rapport_md
    return fichiers
