import json

from src.export.exportation import exporter_resultats
from src.loaders.load_csv import lire_csv
from src.main import executer_pipeline
from tests.jeu_essai import biens


def _lire(chemin):
    return lire_csv(chemin, ";", "utf-8-sig")


def _resultats(propres=(), quarantaine=(), avertissements=(), doublons_probables=()):
    """Un résultat de pipeline construit à la main, pour les cas absents du jeu d'essai."""
    return {
        "propres": list(propres),
        "quarantaine": list(quarantaine),
        "avertissements": list(avertissements),
        "doublons_probables": list(doublons_probables),
        "rapport": {"regles": {}},
    }


def test_exporter_jeu_essai(tmp_path):
    # Jeu d'essai : 9 biens, 1 doublon exact (PLT-00058), HIS-0072 en quarantaine -> 7 propres
    fichiers = exporter_resultats(executer_pipeline(biens), tmp_path)

    assert set(fichiers) == {
        "donnees_propres.csv", "donnees_propres.json", "quarantaine.csv", "quarantaine.json",
        "avertissements.csv", "doublons_probables.csv", "rapport_qualite.json", "resume_regles.csv",
    }
    assert len(_lire(tmp_path / "donnees_propres.csv")) == 7
    assert len(json.loads((tmp_path / "donnees_propres.json").read_text(encoding="utf-8"))) == 7

    quarantaine = _lire(tmp_path / "quarantaine.csv")
    assert len(quarantaine) == 1
    assert quarantaine[0]["id_local"] == "HIS-0072"
    assert quarantaine[0]["prix"] == "N/A"                  # la valeur BRUTE, pas None
    assert quarantaine[0]["motifs"] == "Le prix doit être présent et supérieur à zéro"

    assert len(_lire(tmp_path / "resume_regles.csv")) == 14
    rapport = json.loads((tmp_path / "rapport_qualite.json").read_text(encoding="utf-8"))
    assert rapport["total_recus"] == 9


def test_quarantaine_plusieurs_motifs(tmp_path):
    bien = biens[3].copy()
    motifs = ["Le prix doit être présent et supérieur à zéro", "surface illisible : 'quatre-vingt'"]
    exporter_resultats(_resultats(quarantaine=[{"bien": bien, "motifs": motifs}]), tmp_path)

    # CSV : une seule cellule, motifs séparés par « | »
    ligne = _lire(tmp_path / "quarantaine.csv")[0]
    assert ligne["motifs"] == "Le prix doit être présent et supérieur à zéro | surface illisible : 'quatre-vingt'"
    # JSON : les motifs restent une liste
    entree = json.loads((tmp_path / "quarantaine.json").read_text(encoding="utf-8"))[0]
    assert entree["motifs"] == motifs


def test_avertissements_conserve_ou_non(tmp_path):
    conserve, en_quarantaine = biens[0].copy(), biens[3].copy()       # NOT-02192, HIS-0072
    resultats = _resultats(
        propres=[conserve],
        quarantaine=[{"bien": en_quarantaine, "motifs": ["motif"]}],
        avertissements=[("NOT-02192", "salles_bain_atypiques"), ("HIS-0072", "surface_atypique")],
    )
    exporter_resultats(resultats, tmp_path)

    lignes = _lire(tmp_path / "avertissements.csv")
    assert lignes[0] == {"id_local": "NOT-02192", "source": "notaires",
                         "raison": "salles_bain_atypiques", "conserve": "oui"}
    assert lignes[1]["source"] == "historique"
    assert lignes[1]["conserve"] == "non"


def test_doublons_probables_numerotes_par_groupe(tmp_path):
    groupes = [[biens[0], biens[1]], [biens[2], biens[5]]]
    exporter_resultats(_resultats(doublons_probables=groupes), tmp_path)

    lignes = _lire(tmp_path / "doublons_probables.csv")
    assert [(l["groupe"], l["id_local"]) for l in lignes] == [
        ("1", "NOT-02192"), ("1", "HIS-0001"), ("2", "PLT-00002"), ("2", "PLT-00399"),
    ]
