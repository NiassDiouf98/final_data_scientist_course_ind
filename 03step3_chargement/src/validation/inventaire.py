from src.validation.validation import champs_manquants, ids_en_double
from src.constantes import CHAMPS_ATTENDUS
from src.validation.regles import REGLES

def inventorier(biens):
    biens = list(biens)
    manquants = {}
    regles = {
        regle.nom: {"respectee": 0, "violee": 0, "non_evaluable": 0}
        for regle in REGLES
    }
    for bien in biens:
        for champ in champs_manquants(bien, CHAMPS_ATTENDUS):
            manquants[champ] = manquants.get(champ, 0) + 1
        for regle in REGLES:
            resultat = regle.verifier(bien)
            regles[regle.nom][resultat] += 1
    return {
        "lignes": len(biens),
        "ids_en_double": len(ids_en_double(biens)),
        "manquants": manquants,
        "regles": regles,
    }

