from src.validation.validation import champs_manquants, ids_en_double
from src.constantes import CHAMPS_ATTENDUS

def inventorier(biens):
    biens = list(biens)
    compteurs = {}
    for bien in biens:
        for champ in champs_manquants(bien, CHAMPS_ATTENDUS):
            compteurs[champ] = compteurs.get(champ, 0) + 1
    compteurs["ids_en_double"] = len(ids_en_double(biens))
    compteurs["lignes"] = len(biens)
    return compteurs
