from src.constantes import DOSSIER_SOURCES
import openpyxl

def lire_excel(chemin):
    classeur = openpyxl.load_workbook(chemin)
    feuille = classeur["Annonces"]
    donnees = []
    entetes = [cellule.value for cellule in feuille[1]]

    for ligne in feuille.iter_rows(min_row=2, values_only=True):
        donnees.append(dict(zip(entetes, ligne)))

    return donnees

if __name__ == "__main__":
    print(len(lire_excel(DOSSIER_SOURCES / "agence_teranga.xlsx")))
