import json

import pytest

from src.export.ecriture import ecrire_csv, ecrire_json
from src.loaders.load_csv import lire_csv

# tmp_path : dossier temporaire fourni par pytest, neuf pour chaque test.
# Les tests n'écrivent donc jamais dans le vrai dossier sortie/.

BIENS = [
    {"id_local": "NOT-02192", "ville": "Bounkiling", "prix": 320860000.0, "salles_bain": None},
    {"id_local": "AGT-00001", "ville": "Thiès", "prix": 885000, "salles_bain": 2},
]
COLONNES = ["id_local", "ville", "prix", "salles_bain"]


def test_ecrire_csv_relu_a_l_identique(tmp_path):
    chemin = ecrire_csv(BIENS, tmp_path / "biens.csv", COLONNES)

    relus = lire_csv(chemin, ";", "utf-8-sig")

    assert len(relus) == 2
    assert list(relus[0]) == COLONNES                 # ordre des colonnes respecté
    assert relus[1]["ville"] == "Thiès"               # accent conservé
    assert relus[0]["prix"] == "320860000.0"          # tout redevient du texte en CSV
    assert relus[0]["salles_bain"] == ""              # None -> cellule vide


def test_ecrire_csv_commence_par_la_signature_utf8(tmp_path):
    # Sans cette signature (BOM), Excel afficherait « ThiÃ¨s »
    chemin = ecrire_csv(BIENS, tmp_path / "biens.csv", COLONNES)

    assert chemin.read_bytes().startswith(b"\xef\xbb\xbf")


def test_ecrire_csv_cree_le_dossier(tmp_path):
    chemin = ecrire_csv(BIENS, tmp_path / "sortie" / "sous_dossier" / "biens.csv", COLONNES)

    assert chemin.exists()


def test_ecrire_csv_refuse_une_colonne_oubliee(tmp_path):
    # « ville » n'est pas dans les colonnes : on ne la perd pas en silence
    with pytest.raises(ValueError):
        ecrire_csv(BIENS, tmp_path / "biens.csv", ["id_local", "prix", "salles_bain"])


def test_ecrire_json_relu_a_l_identique(tmp_path):
    donnees = {"biens": BIENS, "motifs": ["prix illisible : 'à négocier'"]}

    chemin = ecrire_json(donnees, tmp_path / "rapport" / "donnees.json")

    assert json.loads(chemin.read_text(encoding="utf-8")) == donnees
    assert "Thiès" in chemin.read_text(encoding="utf-8")    # pas de è
