from collections import Counter

DEFINITION_CONFORME = "ni quarantaine, ni avertissement, ni correction"


def _taux(nombre, total):
    """Pourcentage arrondi à 0,1 près, ou None si le total est nul."""
    return round(nombre / total * 100, 1) if total else None


def _compter_regles(journal):
    """Compte respectee / violee / non_evaluable par règle, avec le taux sur les évaluables."""
    comptes = {}
    for entree in journal:
        for nom, verdict in entree["resultats"].items():
            comptes.setdefault(nom, {"respectee": 0, "violee": 0, "non_evaluable": 0})
            comptes[nom][verdict] += 1

    for nom, c in comptes.items():
        evaluables = c["respectee"] + c["violee"]
        c["evaluables"] = evaluables
        c["taux_conformite"] = _taux(c["respectee"], evaluables)
    return comptes


def produire_rapport(biens, journal, doublons_exacts, conflits, doublons_probables, inventaire):
    """Rassemble les indicateurs du §7 dans un dictionnaire."""
    total = len(biens)
    lignes_en_trop = sum(len(groupe) - 1 for groupe in doublons_exacts)

    conserves = [e for e in journal if not e["en_quarantaine"]]
    avec_avertissement = [e for e in conserves if e["avertissements"]]
    conformes = [e for e in conserves if not e["avertissements"] and not e["champs_corriges"]]

    return {
        "total_recus": total,
        "manquants_par_colonne": inventaire["manquants"],
        "doublons_exacts": {
            "nombre": lignes_en_trop,
            "taux": _taux(lignes_en_trop, total),
            "definition_taux": "lignes en trop / nombre total de biens reçus × 100",
        },
        "conflits": len(conflits),
        "doublons_probables": len(doublons_probables),
        "erreurs_conversion_par_champ": dict(
            Counter(champ for e in journal for champ in e["erreurs_conversion"])
        ),
        "regles": _compter_regles(journal),
        "corriges": sum(1 for e in journal if e["champs_corriges"]),
        "quarantaine": sum(1 for e in journal if e["en_quarantaine"]),
        "avec_avertissement": len(avec_avertissement),
        "entierement_conformes": {
            "nombre": len(conformes),
            "taux": _taux(len(conformes), total),
            "definition": DEFINITION_CONFORME,
            "denominateur": "nombre total de biens reçus",
        },
    }
