from src.constantes import DOSSIER_SOURCES, DOSSIER_REFERENTIELS
import csv

def lire_csv(chemin, separateur, encodage):
    with open(chemin, encoding=encodage, newline="") as fichier:
        return list(csv.DictReader(fichier, delimiter=separateur))


def charger_referentiel_geographique():
    lignes = lire_csv(
        DOSSIER_REFERENTIELS / "referentiel_geographique.csv", ",", "utf-8"
    )
    return {ligne["ville"]: ligne["region"] for ligne in lignes}


def charger_referentiel_prix_m2():
    """Renvoie {categorie: (prix_m2_min, prix_m2_max)}.

    Fourchette large, déduite des bornes indicatives :
    le m² le moins cher = prix_min / surface_max, le plus cher = prix_max / surface_min.
    """
    lignes = lire_csv(
        DOSSIER_REFERENTIELS / "referentiel_categories.csv", ",", "utf-8"
    )
    return {
        ligne["categorie"]: (
            float(ligne["prix_min_indicatif"])
            / float(ligne["surface_max_typique"]),
            float(ligne["prix_max_indicatif"])
            / float(ligne["surface_min_typique"]),
        )
        for ligne in lignes
    }


if __name__ == "__main__":
    print(len(lire_csv(DOSSIER_SOURCES / "notaires.csv", ",", "utf-8")))
    print(len(lire_csv(DOSSIER_SOURCES / "import_historique.csv", ";", "latin-1")))
    print(len(lire_csv(DOSSIER_SOURCES / "plateforme_immo_sn.csv", ";", "utf-8")))