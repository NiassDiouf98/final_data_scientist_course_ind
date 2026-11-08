import pytest
import numpy as np
import pandas as pd
from src.main import executer_pipeline
from tests.jeu_essai import biens
from src.constantes import CHAMPS_ATTENDUS
from src.analyse.statistiques import (
    vers_dataframe,
    separer_transactions,
    resumer,
    statistiques_descriptives,
    ajouter_prix_m2,
    resultats_par_groupe,
)


def test_vers_dataframe_nombre_lignes_et_colonnes():
    df = vers_dataframe(biens)

    assert len(df) == 9
    assert set(df.columns) == set(CHAMPS_ATTENDUS)


def test_separer_transactions_nombre_ventes_et_locations():
    df = vers_dataframe(biens)
    ventes, locations = separer_transactions(df)

    assert len(ventes) == 7
    assert len(locations) == 2


def test_resumer_liste_simple():
    resultat = resumer([1, 2, 3, 4, 100])

    assert resultat["nombre"] == 5
    assert resultat["moyenne"] == 22
    assert resultat["mediane"] == 3
    assert resultat["minimum"] == 1
    assert resultat["q1"] == 2
    assert resultat["q3"] == 4
    assert resultat["maximum"] == 100
    assert resultat["ecart_type"] == pytest.approx(43.617, rel=1e-3)


def test_resumer_ignore_nan():
    assert resumer([1, 2, float("nan")])["nombre"] == 2


def test_resumer_liste_vide():
    assert resumer([])["nombre"] == 0


def test_statistiques_ventes_apres_pipeline():
    propres = executer_pipeline(biens)["propres"]
    ventes, _ = separer_transactions(vers_dataframe(propres))
    statistiques = statistiques_descriptives(ventes, colonnes=("prix",))["prix"]

    # HIS-0072 est en quarantaine et un des deux PLT-00058 est dédoublonné.
    assert len(ventes) == 5
    assert statistiques["mediane"] == pytest.approx(57_620_000)


def test_ecart_type_ventes_accord_numpy_pandas():
    propres = executer_pipeline(biens)["propres"]
    ventes, _ = separer_transactions(vers_dataframe(propres))

    assert resumer(ventes["prix"])["ecart_type"] == pytest.approx(ventes["prix"].std())


def test_ajouter_prix_m2_cas_normaux_et_surfaces_invalides():
    df = pd.DataFrame(
        {
            "prix": [1_000_000, 1_000_000, 1_000_000],
            "surface": [50, 0, np.nan],
        }
    )

    resultat = ajouter_prix_m2(df)

    assert resultat.loc[0, "prix_m2"] == pytest.approx(20_000)
    assert np.isnan(resultat.loc[1, "prix_m2"])
    assert np.isnan(resultat.loc[2, "prix_m2"])


def test_ajouter_prix_m2_ventes_propres_plt_00002():
    propres = executer_pipeline(biens)["propres"]
    ventes, _ = separer_transactions(vers_dataframe(propres))
    bien = ventes[ventes["id_local"] == "PLT-00002"]

    resultat = ajouter_prix_m2(bien)

    assert len(resultat) == 1
    assert resultat["prix_m2"].iloc[0] == pytest.approx(643_080.36)


def test_ajouter_prix_m2_ne_modifie_pas_le_dataframe_recu():
    df = pd.DataFrame({"prix": [1_000_000], "surface": [50]})

    ajouter_prix_m2(df)

    assert "prix_m2" not in df.columns


def test_resultats_par_groupe_valeurs_et_tri_par_mediane():
    df = pd.DataFrame(
        {
            "ville": ["Dakar", "Dakar", "Dakar", "Thiès", "Thiès"],
            "prix": [100, 200, 600, 500, 700],
        }
    )

    resultat = resultats_par_groupe(df, "ville", "prix")

    # Thiès (médiane 600) avant Dakar (200) : différent de l'ordre alphabétique
    assert list(resultat.index) == ["Thiès", "Dakar"]
    assert resultat.loc["Dakar"].to_dict() == {
        "nombre": 3,
        "moyenne": 300.0,
        "mediane": 200.0,
    }
    assert resultat.loc["Thiès"].to_dict() == {
        "nombre": 2,
        "moyenne": 600.0,
        "mediane": 600.0,
    }