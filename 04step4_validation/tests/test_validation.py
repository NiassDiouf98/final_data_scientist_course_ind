from tests.jeu_essai import biens
from src.validation.validation import champs_manquants, ids_en_double
from src.constantes import CHAMPS_ATTENDUS


def test_champs_manquants():
    resultat = champs_manquants(biens[3], CHAMPS_ATTENDUS)
    assert resultat == ["prix", "periodicite", "statut"]
    assert "chambres" not in resultat


def test_ids_en_double():
    assert ids_en_double(biens) == {"PLT-00058"}