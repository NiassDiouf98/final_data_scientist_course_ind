from src.constantes import DOSSIER_SOURCES
import json

def lire_json(chemin):
    with open(chemin, encoding="utf-8") as fichier:
        return json.load(fichier)

if __name__ == "__main__":
    print(len(lire_json(DOSSIER_SOURCES / "particuliers.json")))