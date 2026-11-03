from datetime import date, timedelta
from tests.jeu_essai import biens
from src.validation.regles import (
    creer_regle_ville_region,
    date_non_future_si_vendu,
    date_valide,
    id_present,
    prix_atypique,
    prix_positif,
    surface_atypique,
    surface_positive,
    transaction_valide,
    type_bien_reconnu,
)

def test_prix_positif_respectee():
    assert prix_positif.verifier(biens[2]) == "respectee"


def test_prix_positif_obligatoire_violee_si_non_evaluable():
    assert prix_positif.verifier(biens[3]) == "violee"


def test_prix_positif_violee_sur_une_copie():
    bien = biens[2].copy()
    bien["prix"] = "à négocier"
    
    assert prix_positif.verifier(bien) == "violee"


def test_type_bien_reconnu_violee_sur_une_copie():
    bien = biens[6].copy()
    bien["type_bien"] = "Château"
    
    assert type_bien_reconnu.verifier(bien) == "violee"


def test_transaction_valide_violee_sur_une_copie():
    bien = biens[6].copy()
    bien["type_transaction"] = "achat"
    
    assert transaction_valide.verifier(bien) == "violee"


def test_prix_positif_respectee_avec_prix_numerique():
    bien = biens[2].copy()
    bien["prix"] = 150000

    assert prix_positif.verifier(bien) == "respectee"


def test_prix_positif_violee_si_prix_nul():
    bien = biens[2].copy()
    bien["prix"] = 0

    assert prix_positif.verifier(bien) == "violee"


def test_prix_positif_violee_si_prix_negatif():
    bien = biens[2].copy()
    bien["prix"] = -1

    assert prix_positif.verifier(bien) == "violee"


def test_type_bien_reconnu_respectee():
    assert type_bien_reconnu.verifier(biens[2]) == "respectee"


def test_type_bien_reconnu_non_evaluable_si_type_absent():
    bien = biens[2].copy()
    bien["type_bien"] = ""

    assert type_bien_reconnu.verifier(bien) == "non_evaluable"


def test_transaction_valide_respectee():
    assert transaction_valide.verifier(biens[2]) == "respectee"


def test_transaction_valide_violee_si_type_absent():
    bien = biens[2].copy()
    bien["type_transaction"] = ""

    assert transaction_valide.verifier(bien) == "violee"


def test_id_present_respectee_et_violee_si_absent():
    bien = biens[2].copy()
    assert id_present.verifier(bien) == "respectee"

    bien.pop("id_local", None)
    assert id_present.verifier(bien) == "violee"


def test_surface_positive_accepte_une_surface_numerique():
    bien = biens[2].copy()
    bien["surface"] = "75,5"

    assert surface_positive.verifier(bien) == "respectee"


def test_surface_positive_violee_si_surface_nulle_ou_invalide():
    bien = biens[2].copy()
    bien["surface"] = 0
    assert surface_positive.verifier(bien) == "violee"

    bien["surface"] = "inconnue"
    assert surface_positive.verifier(bien) == "violee"


def test_date_valide_accepte_une_date_iso():
    bien = biens[2].copy()
    bien["date"] = "2024-06-15"

    assert date_valide.verifier(bien) == "respectee"


def test_date_valide_violee_si_date_invalide():
    bien = biens[2].copy()
    bien["date"] = "15/06/2024"

    assert date_valide.verifier(bien) == "violee"


def test_prix_atypique_detecte_un_prix_trop_bas_ou_trop_eleve():
    bien = biens[2].copy()
    bien["prix"] = 99_999
    assert prix_atypique.verifier(bien) == "violee"

    bien["prix"] = 2_000_000_001
    assert prix_atypique.verifier(bien) == "violee"


def test_prix_atypique_accepte_les_limites():
    bien = biens[2].copy()
    bien["prix"] = 100_000
    assert prix_atypique.verifier(bien) == "respectee"

    bien["prix"] = 2_000_000_000
    assert prix_atypique.verifier(bien) == "respectee"


def test_surface_atypique_detecte_les_valeurs_hors_limites():
    bien = biens[2].copy()
    bien["surface"] = 4
    assert surface_atypique.verifier(bien) == "violee"

    bien["surface"] = 2_001
    assert surface_atypique.verifier(bien) == "violee"


def test_surface_atypique_accepte_les_limites():
    bien = biens[2].copy()
    bien["surface"] = 5
    assert surface_atypique.verifier(bien) == "respectee"

    bien["surface"] = 2_000
    assert surface_atypique.verifier(bien) == "respectee"


def test_date_non_future_si_vendu():
    bien = biens[2].copy()
    bien["statut"] = "Vendu"
    bien["date"] = (date.today() - timedelta(days=1)).isoformat()
    assert date_non_future_si_vendu.verifier(bien) == "respectee"

    bien["date"] = (date.today() + timedelta(days=1)).isoformat()
    assert date_non_future_si_vendu.verifier(bien) == "violee"


def test_date_future_autorisee_si_non_vendu():
    bien = biens[2].copy()
    bien["statut"] = "En vente"
    bien["date"] = (date.today() + timedelta(days=1)).isoformat()

    assert date_non_future_si_vendu.verifier(bien) == "respectee"


def test_ville_region_coherentes_avec_un_referentiel_fourni():
    regle = creer_regle_ville_region({"Pikine": "Dakar", "Mbour": "Thiès"})
    bien = biens[2].copy()
    bien["ville"] = "Pikine"
    bien["region"] = "Dakar"
    assert regle.verifier(bien) == "respectee"

    bien["ville"] = "Mbour"
    bien["region"] = "Thiès"
    assert regle.verifier(bien) == "respectee"

    bien["region"] = "Dakar"
    bien["ville"] = "Paris"
    assert regle.verifier(bien) == "violee"