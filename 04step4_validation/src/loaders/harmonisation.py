from src.constantes import CHAMPS_ATTENDUS, DOSSIER_SOURCES
from src.loaders.load_csv import lire_csv
from src.loaders.load_json import lire_json
from src.loaders.load_excel import lire_excel
from src.loaders.correspondances import CORRESPONDANCE_NOTAIRES, VALEURS_FIXES_VENTE, CORRESPONDANCE_HISTORIQUES, CORRESPONDANCE_PLATEFORME, CORRESPONDANCE_PARTICULIERS, CORRESPONDANCE_AGENCE, STATUT_VERS_TRANSACTION

def aplatir(dictionnaire, prefixe=""):
    resultat = {}
    for cle, valeur in dictionnaire.items():
        if isinstance(valeur, dict):
            resultat.update(aplatir(valeur, prefixe + cle + "."))
        else:
            resultat[prefixe + cle] = valeur
    return resultat


def harmoniser(ligne, correspondances, source, valeurs_fixes=None):
    if valeurs_fixes is None:
        valeurs_fixes = {}

    donnees_harmonisees = {champ: None for champ in CHAMPS_ATTENDUS}
    donnees_harmonisees["source"] = source

    for champ_source, champ_commun in correspondances.items():
        donnees_harmonisees[champ_commun] = ligne.get(champ_source)

    for champ, valeur in valeurs_fixes.items():
        donnees_harmonisees[champ] = valeur

    return donnees_harmonisees


def charger_notaires():
    lignes = lire_csv(DOSSIER_SOURCES / "notaires.csv", separateur=",", encodage="utf-8")
    return [
        harmoniser(ligne, CORRESPONDANCE_NOTAIRES, "notaires", VALEURS_FIXES_VENTE)
        for ligne in lignes
    ]


def charger_historique():
    lignes = lire_csv(DOSSIER_SOURCES / "import_historique.csv", separateur=";", encodage="latin-1")
    return [
        harmoniser(ligne, CORRESPONDANCE_HISTORIQUES, "historique", VALEURS_FIXES_VENTE)
        for ligne in lignes
    ]

def charger_plateforme():
    lignes = lire_csv(DOSSIER_SOURCES / "plateforme_immo_sn.csv", separateur=";", encodage="utf-8")
    donnees_harmonisees = []
    for ligne in lignes:
        donnee = harmoniser(ligne, CORRESPONDANCE_PLATEFORME, "plateforme")
        donnee["periodicite"] = "mensuel" if ligne["devise"] == "FCFA/mois" else None
        donnees_harmonisees.append(donnee)
    return donnees_harmonisees


def charger_particuliers():
    lignes = lire_json(DOSSIER_SOURCES / "particuliers.json")
    lignes = [aplatir(ligne) for ligne in lignes]
    return [
        harmoniser(ligne, CORRESPONDANCE_PARTICULIERS, "particuliers")
        for ligne in lignes
    ]


def charger_agences():
    lignes = lire_excel(DOSSIER_SOURCES / "agence_teranga.xlsx")
    donnees_harmonisees = []
    for ligne in lignes:
        donnee = harmoniser(ligne, CORRESPONDANCE_AGENCE, "agence")
        statut = ligne.get("Statut")
        donnee["type_transaction"] = STATUT_VERS_TRANSACTION.get(statut)
        donnees_harmonisees.append(donnee)
    return donnees_harmonisees

