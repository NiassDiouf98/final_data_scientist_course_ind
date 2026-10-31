import sys

# 1 - Jeu d'essai : liste de biens
biens = [
    {"source": "notaires","id_local": "NOT-02192","type_bien": "Villa","region": "Sédhiou","ville": "Bounkiling","date": "2019-05-09","prix": 320860000.0,"surface": 392.1,"chambres": 3,"salles_bain": None,"type_transaction": "vente","periodicite": None,"statut": "Vendu"},
    {"source": "historique","id_local": "HIS-0001","type_bien": "Studio","region": "Louga","ville": "Linguère","date": "2019-11-19","prix": "26 620 000","surface": 44.7,"chambres": 2,"salles_bain": 1,"type_transaction": "vente","periodicite": None,"statut": None},
    {"source": "plateforme","id_local": "PLT-00002","type_bien": "Maison","region": "Kolda","ville": "Kolda","date": "2022-09-15","prix": "57.62 millions","surface": 89.6,"chambres": 5,"salles_bain": 3,"type_transaction": "vente","periodicite": None,"statut": "Vendu"},
    {"source": "historique","id_local": "HIS-0072","type_bien": "Terrain","region": "Ziguinchor","ville": "Bignona","date": "2019-10-16","prix": "N/A","surface": 190.8,"chambres": 0,"salles_bain": 0,"type_transaction": "vente","periodicite": None,"statut": None},
    {"source": "agence","id_local": "AGT-00836","type_bien": "Villa","region": "Dakar","ville": "Dakar","date": "24/07/2022","prix": 885000,"surface": 437.9,"chambres": 2,"salles_bain": 1,"type_transaction": "location","periodicite": None,"statut": "Disponible" },
    {"source": "plateforme","id_local": "PLT-00399","type_bien": "Appartement","region": "Sédhiou","ville": "Bounkiling","date": "2021-01-25","prix": 380000,"surface": 136.8,"chambres": 3,"salles_bain": 1,"type_transaction": "location","periodicite": "mensuel","statut": "Loué"},
    {"source": "plateforme","id_local": "PLT-00080","type_bien": "appart","region": "Matam","ville": "Ourossogui","date": "2020-10-23","prix": 41454000,"surface": 103.6,"chambres": 6,"salles_bain": 2,"type_transaction": "vente","periodicite": None,"statut": "En vente"},
    {"source": "plateforme","id_local": "PLT-00058","type_bien": "Appartement","region": "Diourbel","ville": "Mbacké","date": "2024-04-04","prix": 116544000,"surface": 160.2,"chambres": 5,"salles_bain": 2,"type_transaction": "vente","periodicite": None,"statut": "En vente"},
    {"source": "plateforme","id_local": "PLT-00058","type_bien": "Appartement","region": "Diourbel","ville": "Mbacké","date": "2024-04-04","prix": 116544000,"surface": 160.2,"chambres": 5,"salles_bain": 2,"type_transaction": "vente","periodicite": None,"statut": "En vente"
    }
]

# 2 - Constantes : les 7 categories (un set) et un dict
CATEGORIES = {"Appartement", "Studio", "Chambre", "Villa", "Maison", "Terrain", "Local commercial"}
SYNONYMES = {"appart": "Appartement","appartement": "Appartement","appt": "Appartement","studio": "Studio","chambre": "Chambre","chambre simple": "Chambre","villa": "Villa","maison": "Maison","terrain": "Terrain","terrains": "Terrain","local": "Local commercial","local commercial": "Local commercial","bureau": "Local commercial","magasin": "Local commercial",}
CHAMPS_ATTENDUS = ["source","id_local","type_bien","region","ville","date","prix","surface","chambres","salles_bain","type_transaction","periodicite","statut"]
VALEURS_VIDES = {None, "", "N/A"}

# 3 - Fonctions
def filtrer_par_transaction(biens, type_transaction):
    return [bien for bien in biens if bien.get("type_transaction") == type_transaction]
    
def champs_manquants(bien, champs_attendus):
    return [champ for champ in champs_attendus if champ not in bien or bien[champ] in VALEURS_VIDES]

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
    
if __name__ == "__main__":
    # 4 - Essais
    print("==== Filtre par transaction")
    print(len(filtrer_par_transaction(biens, type_transaction="location")))

    print("==== Champs manquants")
    print(champs_manquants(biens[3], CHAMPS_ATTENDUS))
    print(champs_manquants(biens[0], CHAMPS_ATTENDUS))
    print(champs_manquants(biens[1], CHAMPS_ATTENDUS))

    print("==== Conversion des prix")
    print(f"66.74 millions -> {convertir_prix("66.74 millions")}")
    print(f"320860000.0 -> {convertir_prix(320860000.0)}")
    print(f"'26 620 000' -> {convertir_prix("26 620 000")}")
    print(f"18152000 FCFA -> {convertir_prix("18152000 FCFA")}")
    print(f"N/A -> {convertir_prix("N/A")}")
    print(f"à négocier -> {convertir_prix("à négocier")}")
    print(f"None FCFA -> {convertir_prix("None FCFA")}")
    print(f"0 -> {convertir_prix("0")}")

    print("==== Normalisation des types de bien")
    print(f"Appart -> {normaliser_type_bien("Appart")}")
    print(f"studio -> {normaliser_type_bien("studio")}")
    print(f"chambre simple -> {normaliser_type_bien("chambre simple")}")
    print(f"maison -> {normaliser_type_bien("maison")}")
    print(f"terrain -> {normaliser_type_bien("terrain")}")
    print(f"local -> {normaliser_type_bien("local")}")
    print(f"villa -> {normaliser_type_bien("villa")}")

    print("==== Doublons sur les biens")
    print(f"id doublons -> {ids_en_double(biens)}")

    print("==== cle de rappochement")
    print(f"Bien[7] -> {cle_rapprochement(biens[7])}")
    print(f"Bien[8] -> {cle_rapprochement(biens[8])}")
    print(f"Bien[6] -> {cle_rapprochement(biens[6])}")
    copie_bien = biens[6].copy()
    copie_bien["type_bien"] = "APPARTEMENT"
    copie_bien["ville"] = " Ourossogui "
    print(f"Clés identiques après modification de la copie : {cle_rapprochement(copie_bien) == cle_rapprochement(biens[6])}")
    print(f"appart -> {cle_rapprochement({**biens[6], 'type_bien': 'appart'})}")
    print(f"APPARTEMENT -> {cle_rapprochement({**biens[6], 'type_bien': 'APPARTEMENT'})}")
    print(f"Ourossogui -> {cle_rapprochement({**biens[6], 'ville': 'Ourossogui'})}")
