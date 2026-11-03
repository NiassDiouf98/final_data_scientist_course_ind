import pytest
from tests.jeu_essai import biens
from src.processing.traitement import convertir_date, convertir_prix, convertir_surface, normaliser_type_bien, filtrer_par_transaction, cle_rapprochement, normaliser_selon_referentiel, nettoyer_bien
from src.constantes import STATUTS

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


@pytest.mark.parametrize(
    ("valeur", "attendu"),
    [
        ("92,4", 92.4),
        ("1354,0", 1354.0),
        ("quatre-vingt", None),
        ("", None),
        (-30, -30),
    ],
)
def test_convertir_surface(valeur, attendu):
    assert convertir_surface(valeur) == attendu


@pytest.mark.parametrize(
    ("valeur", "attendu"),
    [
        ("24/07/2022", "2022-07-24"),
        ("2019-05-09", "2019-05-09"),
        ("32/13/2024", None),
        (None, None),
    ],
)
def test_convertir_date(valeur, attendu):
    assert convertir_date(valeur) == attendu


def test_normaliser_selon_referentiel():
    villes = ["Kédougou", "Touba", "Joal-Fadiouth"]

    assert normaliser_selon_referentiel("KÉDOUGOU", villes) == "Kédougou"
    assert normaliser_selon_referentiel(" touba ", villes) == "Touba"
    assert normaliser_selon_referentiel("joal-fadiouth", villes) == "Joal-Fadiouth"
    assert normaliser_selon_referentiel("Paris", villes) == "Paris"
    assert normaliser_selon_referentiel("", villes) is None
    assert normaliser_selon_referentiel(None, villes) is None


def test_nettoyer_bien():
    villes = ["Linguère", "Ourossogui", "Bignona", "Bounkiling"]
    regions = ["Louga", "Matam", "Ziguinchor", "Sédhiou"]

    bien_his = next(b for b in biens if "HIS-0001" in b.values())
    nettoye, corrections, erreurs = nettoyer_bien(bien_his, villes, regions, STATUTS)
    assert nettoye["prix"] == 26620000.0
    assert "prix" in corrections

    bien_plt = next(b for b in biens if "PLT-00080" in b.values())
    nettoye, corrections, _ = nettoyer_bien(bien_plt, villes, regions, STATUTS)
    assert nettoye["type_bien"] == "Appartement"
    assert "type_bien" in corrections

    bien_his_vide = next(b for b in biens if "HIS-0072" in b.values())
    nettoye, _, erreurs = nettoyer_bien(bien_his_vide, villes, regions, STATUTS)
    assert nettoye["prix"] is None
    assert "prix" not in erreurs

    bien_surface_invalide = bien_his.copy()
    bien_surface_invalide["surface"] = "quatre-vingt"
    _, _, erreurs = nettoyer_bien(bien_surface_invalide, villes, regions, STATUTS)
    assert "surface" in erreurs

    bien_not = next(b for b in biens if "NOT-02192" in b.values())
    original = bien_not.copy()
    nettoye, corrections, _ = nettoyer_bien(bien_not, villes, regions, STATUTS)
    assert corrections == []
    assert bien_not == original