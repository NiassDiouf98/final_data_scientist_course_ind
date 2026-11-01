from src.constantes import VALEURS_VIDES

SYNONYMES = {
    "appart": "Appartement",
    "appartement": "Appartement",
    "appt": "Appartement",
    "studio": "Studio",
    "chambre": "Chambre",
    "chambre simple": "Chambre",
    "villa": "Villa",
    "maison": "Maison",
    "terrain": "Terrain",
    "terrains": "Terrain",
    "local": "Local commercial",
    "local commercial": "Local commercial",
    "bureau": "Local commercial",
    "magasin": "Local commercial",
}

def filtrer_par_transaction(biens, type_transaction):
    return [bien for bien in biens if bien.get("type_transaction") == type_transaction]
    

def convertir_prix(prix):
    if isinstance(prix, (int, float)):
        return prix
    if prix in VALEURS_VIDES:
        return None

    texte = str(prix).strip().replace("FCFA", "").replace("fcfa", "")
    texte = "".join(texte.split())
    millions = "million" in texte.lower()
    texte = texte.lower().replace("millions", "")

    try:
        valeur = float(texte)
    except ValueError:
        return None
    return round(valeur * 1_000_000) if millions else valeur


def normaliser_type_bien(type_bien):
    if not isinstance(type_bien, str):
        return None
    type_normalise = type_bien.strip().lower()
    return SYNONYMES.get(type_normalise, type_bien.strip())


# Limite connue : les dates ne sont pas encore normalisées.
def cle_rapprochement(bien):
    ville = bien.get("ville")
    ville_normalisee = ville.strip().lower() if isinstance(ville, str) else ville
    return (
        normaliser_type_bien(bien.get("type_bien")),
        ville_normalisee,
        bien.get("surface"),
        bien.get("date"),
    )