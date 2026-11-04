from tests.jeu_essai import biens
from src.constantes import STATUTS
from src.loaders.load_csv import charger_referentiel_geographique
from src.validation.regles import REGLES, creer_regle_ville_region
from src.validation.separation import separer_biens
from src.validation.doublons import detecter_doublons
from src.validation.inventaire import inventorier
from src.validation.rapport import produire_rapport

referentiel = charger_referentiel_geographique()
villes = list(referentiel)
regions = set(referentiel.values())
regles = REGLES + [creer_regle_ville_region(referentiel)]


def _rapport(liste):
    propres, _, _, journal = separer_biens(liste, regles, villes, regions, STATUTS)
    _, doublons_exacts, conflits, doublons_probables = detecter_doublons(propres)
    return produire_rapport(
        liste, journal, doublons_exacts, conflits, doublons_probables, inventorier(liste)
    )


def test_rapport_jeu_essai_compteurs_generaux():
    rapport = _rapport(biens)

    assert rapport["total_recus"] == 9
    assert rapport["quarantaine"] == 1                       # HIS-0072
    assert rapport["doublons_exacts"]["nombre"] == 1         # PLT-00058
    assert rapport["doublons_exacts"]["taux"] == 11.1        # 1 / 9
    assert rapport["conflits"] == 0
    assert rapport["doublons_probables"] == 0
    assert rapport["erreurs_conversion_par_champ"] == {}
    assert rapport["corriges"] == 4                          # HIS-0001, PLT-00002, AGT-00836, PLT-00080
    assert rapport["avec_avertissement"] == 0


def test_date_valide_compte_sur_les_biens_nettoyes():
    # Brut : 8/1/0 (AGT-00836 en JJ/MM/AAAA). Nettoyé : la date est normalisée.
    rapport = _rapport(biens)

    assert rapport["regles"]["date_valide"] == {
        "respectee": 9, "violee": 0, "non_evaluable": 0,
        "evaluables": 9, "taux_conformite": 100.0,
    }


def test_non_evaluable_exclu_du_denominateur():
    # HIS-0072 (prix « N/A ») et les locations AGT-00836 et PLT-00399 : non évaluables
    rapport = _rapport(biens)

    assert rapport["regles"]["prix_atypique"] == {
        "respectee": 6, "violee": 0, "non_evaluable": 3,
        "evaluables": 6, "taux_conformite": 100.0,
    }


def test_entierement_conformes_definition_stricte():
    # NOT-02192, PLT-00399 et les deux PLT-00058 : ni quarantaine, ni avertissement, ni correction
    rapport = _rapport(biens)

    assert rapport["entierement_conformes"]["nombre"] == 4
    assert rapport["entierement_conformes"]["taux"] == 44.4


def test_un_bien_avec_deux_avertissements_compte_une_fois():
    bien = biens[0].copy()                 # NOT-02192, conforme
    bien["prix"] = 50_000                  # prix_atypique
    bien["surface"] = 3                    # surface_atypique
    rapport = _rapport([bien])

    assert rapport["avec_avertissement"] == 1
    assert rapport["quarantaine"] == 0
    assert rapport["entierement_conformes"]["nombre"] == 0


def test_erreur_de_conversion_comptee_par_champ():
    bien = biens[0].copy()
    bien["prix"] = "à négocier"
    rapport = _rapport([bien])

    assert rapport["erreurs_conversion_par_champ"] == {"prix": 1}
    assert rapport["quarantaine"] == 1
