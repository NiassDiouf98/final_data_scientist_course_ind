from tests.jeu_essai import biens
from src.validation.inventaire import inventorier
from src.validation.regles import chambres_atypiques, loyer_atypique, salles_bain_atypiques

def test_inventaire():
    inventaire = inventorier(biens)

    attendu = {
        "lignes": 9,
        "ids_en_double": 1,
        "manquants": {"prix": 1, "salles_bain": 1, "periodicite": 8, "statut": 2},
        "regles": {
            "prix_positif": {"respectee": 8, "violee": 1, "non_evaluable": 0},
            "type_bien_reconnu": {"respectee": 9, "violee": 0, "non_evaluable": 0},
            "transaction_valide": {"respectee": 9, "violee": 0, "non_evaluable": 0},
            "id_present": {"respectee": 9, "violee": 0, "non_evaluable": 0},
            "surface_positive": {"respectee": 9, "violee": 0, "non_evaluable": 0},
            "prix_atypique": {"respectee": 6, "violee": 0, "non_evaluable": 3},
            "surface_atypique": {"respectee": 9, "violee": 0, "non_evaluable": 0},
            "date_non_future_si_vendu": {"respectee": 9, "violee": 0, "non_evaluable": 0},
            "date_valide": {"respectee": 8, "violee": 1, "non_evaluable": 0},
            "loyer_atypique": {"respectee": 2, "violee": 0, "non_evaluable": 7},
            "chambres_atypiques": {"respectee": 5, "violee": 0, "non_evaluable": 4},
            "salles_bain_atypiques": {"respectee": 7, "violee": 0, "non_evaluable": 2},
        },
    }

    assert inventaire == attendu


def test_salles_bain_atypiques_local_commercial_non_evaluable():
    bien = biens[0].copy()
    bien.update({"type_bien": "Local commercial", "chambres": 0, "salles_bain": 4})

    assert salles_bain_atypiques.verifier(bien) == "non_evaluable"



def test_salles_bain_atypiques_appartement_violee():
    bien = biens[0].copy()
    bien.update({"type_bien": "Appartement", "chambres": 1, "salles_bain": 4})

    assert salles_bain_atypiques.verifier(bien) == "violee"


def test_loyer_atypique_vente_non_evaluable():
    bien = biens[0].copy()
    bien.update({"type_transaction": "vente", "prix": 20_000})

    assert loyer_atypique.verifier(bien) == "non_evaluable"


def test_loyer_atypique_loyer_bas_violee():
    bien = biens[0].copy()
    bien.update({"type_transaction": "location", "prix": 20_000})

    assert loyer_atypique.verifier(bien) == "violee"


def test_loyer_atypique_loyer_tres_eleve_violee():
    bien = biens[0].copy()
    bien.update({"type_transaction": "location", "prix": 6_000_000})

    assert loyer_atypique.verifier(bien) == "violee"


def test_chambres_atypiques_appartement_12_violee():
    bien = biens[0].copy()
    bien.update({"type_bien": "Appartement", "chambres": 12})

    assert chambres_atypiques.verifier(bien) == "violee"


def test_chambres_atypiques_villa_12_non_evaluable():
    bien = biens[0].copy()
    bien.update({"type_bien": "Villa", "chambres": 12})

    assert chambres_atypiques.verifier(bien) == "non_evaluable"