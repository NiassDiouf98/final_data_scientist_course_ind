from src.constantes import DOSSIER_SOURCES
from src.loaders.load_csv import lire_csv

def test_lire_csv():
    donnees = lire_csv(DOSSIER_SOURCES / "notaires.csv", ",", "utf-8")

    assert len(donnees) == 410
    assert donnees[0]["id_acte"] == "NOT-02192"
    assert donnees[0]["montant_fcfa"] == "320860000.0"


def test_lire_json():
    from src.loaders.load_json import lire_json

    donnees = lire_json(DOSSIER_SOURCES / "particuliers.json")

    assert len(donnees) == 731
    assert donnees[0]["annonce"]["id"] == "PRT-01461"
    assert donnees[0]["annonce"]["details"]["prix"] == 18152000


def test_lire_excel():
    from src.loaders.load_excel import lire_excel

    donnees = lire_excel(DOSSIER_SOURCES / "agence_teranga.xlsx")

    assert len(donnees) == 640
    assert donnees[0]["Code"] == "AGT-00821"
    assert donnees[0]["Prix_FCFA"] == 38448000