from src.constantes import DOSSIER_SOURCES
import csv

def lire_csv(chemin, separateur, encodage):
    with open(chemin, encoding=encodage, newline="") as fichier:
        return list(csv.DictReader(fichier, delimiter=separateur))

if __name__ == "__main__":
    print(len(lire_csv(DOSSIER_SOURCES / "notaires.csv", ",", "utf-8")))
    print(len(lire_csv(DOSSIER_SOURCES / "import_historique.csv", ";", "utf-8")))
    print(len(lire_csv(DOSSIER_SOURCES / "plateforme_immo_sn.csv", ";", "utf-8")))