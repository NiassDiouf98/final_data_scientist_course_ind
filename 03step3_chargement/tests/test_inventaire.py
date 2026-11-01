from tests.jeu_essai import biens
from src.validation.inventaire import inventorier

def test_inventaire():
    inventaire = inventorier(biens)

    attendu = {
        "lignes": 9,
        "ids_en_double": 1,
        "prix": 1,
        "salles_bain": 1,
        "periodicite": 8,
        "statut": 2
    }

    assert inventaire == attendu