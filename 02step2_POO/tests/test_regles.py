from tests.jeu_essai import biens
from src.validation.regles import prix_positif, type_bien_reconnu, transaction_valide

def test_prix_positif_respectee():
    assert prix_positif.verifier(biens[2]) == "respectee"


def test_prix_positif_non_evaluable():
    assert prix_positif.verifier(biens[3]) == "non_evaluable"


def test_prix_positif_violee_sur_une_copie():
    bien = biens[2].copy()
    bien["prix"] == "à négocier"
    
    assert prix_positif.verifier(bien) == "violee"


def test_type_bien_reconnu_violee_sur_une_copie():
    bien = biens[6].copy()
    bien["type_bien"] = "Château"
    
    assert type_bien_reconnu.verifier(bien) == "violee"


def test_transaction_valide_violee_sur_une_copie():
    bien = biens[6].copy()
    bien["transaction"] = "achat"
    
    assert transaction_valide.verifier(bien) == "violee"