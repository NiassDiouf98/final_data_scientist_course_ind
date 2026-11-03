# Table de correspondance entre les noms de colonnes dans le fichier CSV des notaires et
# les noms de colonnes attendus dans le format harmonisé.
CORRESPONDANCE_NOTAIRES = {
    "id_acte": "id_local",
    "date_acte": "date",
    "region": "region",
    "ville": "ville",
    "type_bien": "type_bien",
    "montant_fcfa": "prix",
    "superficie": "surface",
    "nb_chambres": "chambres",
    "statut": "statut",
}

VALEURS_FIXES_VENTE = {"type_transaction": "vente"}

# Table de correspondance entre les noms de colonnes dans le fichier CSV des historiques et
# les noms de colonnes attendus dans le format harmonisé.
CORRESPONDANCE_HISTORIQUES = {
    "ID": "id_local",
    "DateVente": "date",
    "Region": "region",
    "Ville": "ville",
    "TypeBien": "type_bien",
    "Prix": "prix",
    "Surface": "surface",
    "Chambres": "chambres",
    "SallesBain": "salles_bain",
}

# Table de correspondance entre les noms de colonnes dans le fichier CSV de la plateforme 
# immobilière et les noms de colonnes attendus dans le format harmonisé.
CORRESPONDANCE_PLATEFORME = {
    "ref_plateforme": "id_local",
    "date_mise_en_ligne": "date",
    "type_transaction": "type_transaction",
    "categorie": "type_bien",
    "region": "region",
    "commune": "ville",
    "prix": "prix",
    "surface": "surface",
    "pieces": "chambres",
    "sdb": "salles_bain",
    "statut": "statut",
}

# Table de correspondance entre les noms de colonnes dans le fichier json de particuliers
# et les noms de colonnes attendus dans le format harmonisé.
CORRESPONDANCE_PARTICULIERS = {
    "annonce.id": "id_local",
    "annonce.date": "date",
    "annonce.localisation.region": "region",
    "annonce.localisation.ville": "ville",
    "annonce.details.type": "type_bien",
    "annonce.details.transaction": "type_transaction",
    "annonce.details.prix": "prix",
    "annonce.details.surface": "surface",
    "annonce.details.chambres": "chambres",
    "annonce.details.sdb": "salles_bain",
    "annonce.statut": "statut",
}

# Table de correspondance entre les noms de colonnes dans le fichier excel de l'agence
# et les noms de colonnes attendus dans le format harmonisé.
CORRESPONDANCE_AGENCE = {
    "Code": "id_local",
    "Date": "date",
    "Region": "region",
    "Ville": "ville",
    "Type": "type_bien",
    "Prix_FCFA": "prix",
    "Surface_m2": "surface",
    "Chambres": "chambres",
    "SDB": "salles_bain",
    "Statut": "statut",
}

STATUT_VERS_TRANSACTION = {
    "Vendu": "vente",
    "En vente": "vente",
    "Disponible": "location",
    "Loué": "location",
}