from tests.jeu_essai import biens
from src.validation.inventaire import inventorier

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
            "prix_atypique": {"respectee": 8, "violee": 0, "non_evaluable": 1},
            "surface_atypique": {"respectee": 9, "violee": 0, "non_evaluable": 0},
            "date_non_future_si_vendu": {"respectee": 9, "violee": 0, "non_evaluable": 0},
            "date_valide": {"respectee": 8, "violee": 1, "non_evaluable": 0},
        },
    }

    assert inventaire == attendu