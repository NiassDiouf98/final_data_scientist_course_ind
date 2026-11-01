from tests.jeu_essai import biens
from src.processing.traitement import convertir_prix, normaliser_type_bien, filtrer_par_transaction, cle_rapprochement

def test_filter_locations():
    resultat = filtrer_par_transaction(biens, "location")
    assert len(resultat) == 2


def test_convertir_prix_conformes():
    assert convertir_prix(320860000.0) == 320860000.0
    assert convertir_prix("26 620 000") == 26620000.0
    assert convertir_prix("18152000 FCFA") == 18152000.0
    assert convertir_prix("57.62 millions") == 57620000.0


def test_convertir_prix_limites():
    assert convertir_prix("66.74 millions") == 66740000.0
    assert convertir_prix("0") == 0.0


def test_convertir_prix_invalides():
    assert convertir_prix("N/A") is None
    assert convertir_prix("à négocier") is None
    assert convertir_prix("None FCFA") is None


def test_normaliser_type_bien():
    assert normaliser_type_bien("Villa") == "Villa"
    assert normaliser_type_bien("APPARTEMENT") == "Appartement"
    assert normaliser_type_bien("appart") == "Appartement"
    assert normaliser_type_bien(" Studio ") == "Studio"
    assert normaliser_type_bien("bureau") == "Local commercial"
    assert normaliser_type_bien("Château") == "Château"
    assert normaliser_type_bien(None) is None
    

def test_cle_rapprochement():
    copie = biens[6].copy()
    copie["type_bien"] = "APPARTEMENT"
    copie["ville"] = " Ourossogui "
    assert cle_rapprochement(biens[6]) == cle_rapprochement(copie)
    assert biens[6]["type_bien"] == "appart"
