from src.constantes import VALEURS_VIDES

CATEGORIES = {"Appartement", "Studio", "Chambre", "Villa", "Maison", "Terrain", "Local commercial"}

def champs_manquants(bien, champs_attendus):
    return [champ for champ in champs_attendus if champ not in bien or bien[champ] in VALEURS_VIDES]


def ids_en_double(biens):
    ids_vus = set()
    doublons = set()
    for bien in biens:
        identifiant = bien.get("id_local")
        if identifiant in VALEURS_VIDES:
            continue
        if identifiant in ids_vus:
            doublons.add(identifiant)
        else:
            ids_vus.add(identifiant)
    return doublons