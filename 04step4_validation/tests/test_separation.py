from tests.jeu_essai import biens
from src.validation.regles import REGLES, creer_regle_ville_region
from src.loaders.load_csv import charger_referentiel_geographique
from src.validation.separation import separer_biens
from src.constantes import STATUTS

referentiel = charger_referentiel_geographique()
villes = list(referentiel)
regions = set(referentiel.values())
regles = REGLES + [creer_regle_ville_region(referentiel)]


def _separer(annonces):
    return separer_biens(annonces, regles, villes, regions, STATUTS)


def test_his_0072_est_mis_en_quarantaine_pour_son_prix_invalide():
    annonce = next(bien for bien in biens if bien["id_local"] == "HIS-0072")
    propres, quarantaine, avertissements, _ = _separer([annonce])

    assert len(propres) == 0
    assert len(quarantaine) == 1
    assert quarantaine[0]["bien"]["id_local"] == "HIS-0072"
    assert quarantaine[0]["motifs"] == ["Le prix doit être présent et supérieur à zéro"]
    assert avertissements == []


def test_jeu_essai_complet_separe_huit_biens_propres_et_his_0072_en_quarantaine():
    propres, quarantaine, _, _ = _separer(biens)

    assert len(propres) == 8
    assert len(quarantaine) == 1
    assert quarantaine[0]["bien"]["id_local"] == "HIS-0072"


def test_prix_illisible_est_signale_exactement():
    annonce = next(bien for bien in biens if bien["id_local"] == "AGT-00836").copy()
    annonce["prix"] = "à négocier"
    _, quarantaine, _, _ = _separer([annonce])

    assert len(quarantaine) == 1
    assert quarantaine[0]["motifs"] == ["prix illisible : 'à négocier'"]


def test_agt_00836_du_jeu_essai_est_propre_apres_normalisation():
    annonce = next(bien for bien in biens if bien["id_local"] == "AGT-00836")
    propres, quarantaine, _, _ = _separer([annonce])

    assert len(propres) == 1
    assert propres[0]["id_local"] == "AGT-00836"
    assert len(quarantaine) == 0
