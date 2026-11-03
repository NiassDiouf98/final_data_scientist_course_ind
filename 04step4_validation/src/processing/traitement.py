from src.constantes import VALEURS_VIDES
from datetime import datetime

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
        bien.get("type_transaction"),
    )


def convertir_surface(valeur):
    if isinstance(valeur, (int, float)):
        return valeur
    if valeur in VALEURS_VIDES:
        return None

    texte = str(valeur).replace(",", ".")
    texte = "".join(texte.split())

    try:
        return float(texte)
    except ValueError:
        return None


def convertir_date(valeur):
    if valeur in VALEURS_VIDES:
        return None

    texte = str(valeur).strip()
    for format_date in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(texte, format_date).date().isoformat()
        except ValueError:
            continue

    return None


def normaliser_selon_referentiel(valeur, valeurs_officielles):
    if valeur in VALEURS_VIDES:
        return None

    texte = str(valeur).strip()
    if not texte:
        return None

    referentiel = {
        officiel.lower(): officiel for officiel in valeurs_officielles
    }
    return referentiel.get(texte.lower(), texte)


def valeur_presente(valeur):
    return valeur not in VALEURS_VIDES


def _est_nombre_direct(valeur):
    if isinstance(valeur, (int, float)):
        return True
    try:
        float(valeur)
        return True
    except (TypeError, ValueError):
        return False


def nettoyer_bien(bien, villes, regions, statuts):
    bien_nettoye = bien.copy()
    champs_corriges = []
    erreurs_conversion = []


    # Nettoyage des champs numeriques
    for champ, convertisseur in (("prix", convertir_prix), ("surface", convertir_surface)):
        valeur_brute = bien.get(champ)
        valeur_nettoyee = convertisseur(valeur_brute)
        bien_nettoye[champ] = valeur_nettoyee
        if valeur_presente(valeur_brute) and valeur_nettoyee is None:
            erreurs_conversion.append(champ)
        elif valeur_nettoyee is not None and not _est_nombre_direct(valeur_brute):
            champs_corriges.append(champ)

    conversions = (
        ("date", convertir_date),
        ("type_bien", normaliser_type_bien),
        ("ville", lambda valeur: normaliser_selon_referentiel(valeur, villes)),
        ("region", lambda valeur: normaliser_selon_referentiel(valeur, regions)),
        ("statut", lambda valeur: normaliser_selon_referentiel(valeur, statuts)),
    )
    for champ, convertisseur in conversions:
        valeur_brute = bien.get(champ)
        valeur_nettoyee = convertisseur(valeur_brute)
        bien_nettoye[champ] = valeur_nettoyee
        if valeur_presente(valeur_brute) and valeur_nettoyee is None:
            erreurs_conversion.append(champ)
        elif valeur_nettoyee != valeur_brute:
            champs_corriges.append(champ)

    for champ in ("chambres", "salles_bain"):
        valeur_brute = bien.get(champ)
        if not valeur_presente(valeur_brute):
            bien_nettoye[champ] = None
            continue
        try:
            valeur_nettoyee = int(valeur_brute)
        except (TypeError, ValueError, OverflowError):
            valeur_nettoyee = None

        bien_nettoye[champ] = valeur_nettoyee
        if valeur_nettoyee is None:
            erreurs_conversion.append(champ)
        elif not _est_nombre_direct(valeur_brute):
            champs_corriges.append(champ)

    return bien_nettoye, champs_corriges, erreurs_conversion