from tests.jeu_essai import biens
from src.validation.doublons import detecter_doublons


def test_huit_biens_uniques_et_un_doublon_exact():
    biens_uniques, doublons_exacts, conflits, doublons_probables = detecter_doublons(biens)

    assert len(biens_uniques) == 8
    assert doublons_exacts == [[biens[-2], biens[-1]]]
    assert conflits == []
    assert doublons_probables == []


def test_meme_identifiant_avec_un_prix_different_est_un_conflit():
    conflit = biens[-1].copy()
    conflit["prix"] = 120000000
    liste = biens + [conflit]

    biens_uniques, doublons_exacts, conflits, doublons_probables = detecter_doublons(
        liste
    )

    assert len(biens_uniques) == 7
    assert doublons_exacts == []
    assert conflits == [[biens[-2], biens[-1], conflit]]
    assert doublons_probables == []


def test_autre_source_meme_type_ville_et_surface_est_probable():
    probable = biens[-1].copy()
    probable["source"] = "agence"
    probable["id_local"] = "AGT-00058"
    liste = biens + [probable]

    biens_uniques, doublons_exacts, conflits, doublons_probables = detecter_doublons(
        liste
    )

    assert len(biens_uniques) == 9
    assert doublons_exacts == [[biens[-2], biens[-1]]]
    assert conflits == []
    assert doublons_probables == [[biens[-1], probable]]


def test_autre_source_autre_id_et_autre_date_est_probable():
    probable = biens[-1].copy()
    probable["source"] = "agence"
    probable["id_local"] = "AGT-00058"
    probable["date"] = "2025-06-01"
    liste = biens + [probable]

    biens_uniques, doublons_exacts, conflits, doublons_probables = detecter_doublons(
        liste
    )

    assert len(biens_uniques) == 9
    assert doublons_exacts == [[biens[-2], biens[-1]]]
    assert conflits == []
    assert doublons_probables == [[biens[-1], probable]]


def test_autre_source_autre_id_et_location_n_est_pas_probable():
    location = biens[-1].copy()
    location["source"] = "agence"
    location["id_local"] = "AGT-00058"
    location["type_transaction"] = "location"
    liste = biens + [location]

    biens_uniques, doublons_exacts, conflits, doublons_probables = detecter_doublons(
        liste
    )

    assert len(biens_uniques) == 9
    assert doublons_exacts == [[biens[-2], biens[-1]]]
    assert conflits == []
    assert doublons_probables == []
