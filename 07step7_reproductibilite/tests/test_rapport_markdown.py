import json

from src.export.exportation import exporter_tout
from src.export.rapport_markdown import produire_rapport_markdown
from src.loaders.load_csv import lire_csv
from src.main import executer_pipeline, main
from tests.jeu_essai import biens


def test_rapport_markdown_jeu_essai():
    texte = produire_rapport_markdown(biens, executer_pipeline(biens))

    for titre in ["# Rapport de qualité", "## Synthèse", "## Par source", "## Quarantaine",
                  "## Valeurs manquantes par colonne", "## Conformité par règle", "## Doublons"]:
        assert titre in texte
    assert "| Biens reçus | 9 |" in texte
    assert "| Mis en quarantaine | 1 | 11,1 % |" in texte
    assert "| Le prix doit être présent et supérieur à zéro | 1 |" in texte
    # 2 locations : AGT-00836 sans périodicité, PLT-00399 mensuelle
    assert "Elle manque vraiment pour 1 locations sur 2 (50,0 %)" in texte


def test_rapport_markdown_identique_d_une_execution_a_l_autre():
    # Pas de date ni d'ordre aléatoire : deux exécutions donnent le même fichier
    assert produire_rapport_markdown(biens, executer_pipeline(biens)) == \
        produire_rapport_markdown(biens, executer_pipeline(biens))


def test_exporter_tout_ajoute_le_rapport_markdown(tmp_path):
    fichiers = exporter_tout(biens, executer_pipeline(biens), tmp_path)

    assert len(fichiers) == 9
    assert (tmp_path / "rapport_qualite.md").read_text(encoding="utf-8").startswith("# Rapport de qualité")


def test_main_de_bout_en_bout(tmp_path):
    # Critère n° 10 : tout le pipeline, sur les vraies sources, avec une seule fonction.
    # On vérifie ensuite les fichiers produits en les relisant.
    main(dossier_sortie=tmp_path)

    propres = lire_csv(tmp_path / "donnees_propres.csv", ";", "utf-8-sig")
    quarantaine = lire_csv(tmp_path / "quarantaine.csv", ";", "utf-8-sig")
    rapport = json.loads((tmp_path / "rapport_qualite.json").read_text(encoding="utf-8"))

    assert rapport["total_recus"] == 3184
    assert len(quarantaine) == rapport["quarantaine"] == 187
    assert all(ligne["motifs"] for ligne in quarantaine)          # chaque ligne a une justification
    # Reçus = propres uniques + quarantaine + doublons exacts retirés
    assert len(propres) + len(quarantaine) + rapport["doublons_exacts"]["nombre"] == 3184
