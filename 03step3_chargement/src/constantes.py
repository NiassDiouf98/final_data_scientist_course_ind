from pathlib import Path

VALEURS_VIDES = {None, "", "N/A"}
CHAMPS_ATTENDUS = ["source","id_local","type_bien","region","ville","date","prix","surface","chambres","salles_bain","type_transaction","periodicite","statut"]
DOSSIER_SOURCES = Path(__file__).resolve().parents[2] / "sources"