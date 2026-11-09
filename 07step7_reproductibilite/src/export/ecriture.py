import csv
import json
from pathlib import Path

# Point-virgule : la virgule est le séparateur décimal en français, et Excel (réglé en français)
# découpe les colonnes au point-virgule. C'est aussi le séparateur de la plateforme et de l'historique.
SEPARATEUR_CSV = ";"
# utf-8-sig ajoute une signature (BOM) en tête de fichier : sans elle, Excel lit le fichier
# comme du Windows-1252 et affiche « ThiÃ¨s » au lieu de « Thiès ».
ENCODAGE_CSV = "utf-8-sig"


def ecrire_csv(lignes, chemin, colonnes):
    """Écrit une liste de dictionnaires en CSV, une ligne par dictionnaire.

    colonnes fixe l'ordre des colonnes. Une valeur None devient une cellule vide.
    Une clé absente de colonnes lève une ValueError : on ne perd pas une donnée sans le savoir.
    Crée le dossier s'il n'existe pas, et renvoie le chemin du fichier.
    """
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, "w", encoding=ENCODAGE_CSV, newline="") as fichier:
        ecrivain = csv.DictWriter(fichier, fieldnames=colonnes, delimiter=SEPARATEUR_CSV)
        ecrivain.writeheader()
        ecrivain.writerows(lignes)
    return chemin


def ecrire_texte(texte, chemin):
    """Écrit un texte (Markdown…) en UTF-8. Crée le dossier s'il n'existe pas, et renvoie le chemin."""
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(texte, encoding="utf-8")
    return chemin


def ecrire_json(objet, chemin):
    """Écrit un objet (liste, dictionnaire…) en JSON lisible, accents conservés.

    Crée le dossier s'il n'existe pas, et renvoie le chemin du fichier.
    """
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as fichier:
        json.dump(objet, fichier, ensure_ascii=False, indent=2)
    return chemin
