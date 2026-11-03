from collections import Counter

from src.constantes import STATUTS
from src.loaders.harmonisation import ( charger_agences, charger_historique, charger_notaires, charger_particuliers, charger_plateforme )
from src.loaders.load_csv import charger_referentiel_geographique
from src.validation.doublons import detecter_doublons
from src.validation.inventaire import inventorier
from src.validation.rapport import produire_rapport
from src.validation.regles import REGLES, creer_regle_ville_region
from src.validation.separation import separer_biens

CHARGEURS = {
    "plateforme": charger_plateforme,
    "agence": charger_agences,
    "particuliers": charger_particuliers,
    "notaires": charger_notaires,
    "historique": charger_historique,
}


def charger_tout():
    """Charge les 5 sources et renvoie une seule liste de biens au format commun."""
    biens = []
    for chargeur in CHARGEURS.values():
        biens.extend(chargeur())
    return biens


def executer_pipeline(biens):
    """Normalise, valide, sépare et dédoublonne. Renvoie les résultats et le rapport."""
    referentiel = charger_referentiel_geographique()
    villes = list(referentiel)
    regions = set(referentiel.values())
    regles = REGLES + [creer_regle_ville_region(referentiel)]

    propres, quarantaine, avertissements, journal = separer_biens(
        biens, regles, villes, regions, STATUTS
    )
    biens_uniques, doublons_exacts, conflits, doublons_probables = detecter_doublons(propres)

    # Un conflit d'identifiant ne peut pas être tranché : ses biens vont en quarantaine
    for groupe in conflits:
        for bien in groupe:
            quarantaine.append({"bien": bien, "motifs": ["Conflit d'identifiant"]})

    rapport = produire_rapport(
        biens, journal, doublons_exacts, conflits, doublons_probables, inventorier(biens)
    )
    return {
        "propres": biens_uniques,
        "quarantaine": quarantaine,
        "avertissements": avertissements,
        "doublons_probables": doublons_probables,
        "rapport": rapport,
    }


def afficher(resultats):
    """Affiche le rapport qualité sous forme lisible."""
    r = resultats["rapport"]
    total = r["total_recus"]

    print("=== RAPPORT QUALITÉ ===\n")
    print(f"Biens reçus                     : {total}")
    print(f"Biens propres (après doublons)  : {len(resultats['propres'])}")
    print(f"Mis en quarantaine              : {r['quarantaine']}")
    print(f"Conservés avec avertissement    : {r['avec_avertissement']}")
    print(f"Corrigés                        : {r['corriges']}")
    conformes = r["entierement_conformes"]
    print(f"Entièrement conformes           : {conformes['nombre']} ({conformes['taux']} %)")
    print(f"   définition : {conformes['definition']}")

    d = r["doublons_exacts"]
    print(f"\nDoublons exacts                 : {d['nombre']} ({d['taux']} %, {d['definition_taux']})")
    print(f"Conflits d'identifiant          : {r['conflits']}")
    print(f"Doublons probables (signalés)   : {r['doublons_probables']}")

    print("\nErreurs de conversion par champ :")
    for champ, nombre in sorted(r["erreurs_conversion_par_champ"].items()):
        print(f"   {champ:<12} {nombre}")

    print("\nValeurs manquantes par colonne :")
    for champ, nombre in sorted(r["manquants_par_colonne"].items()):
        print(f"   {champ:<12} {nombre}")

    print("\nRègles (taux = respectées / évaluables) :")
    print(f"   {'règle':<26} {'respectée':>9} {'violée':>7} {'non éval.':>9} {'taux':>7}")
    for nom, c in r["regles"].items():
        taux = "—" if c["taux_conformite"] is None else f"{c['taux_conformite']} %"
        print(f"   {nom:<26} {c['respectee']:>9} {c['violee']:>7} {c['non_evaluable']:>9} {taux:>7}")

    print("\nMotifs de quarantaine :")
    motifs = Counter(m for q in resultats["quarantaine"] for m in q["motifs"])
    for motif, nombre in motifs.most_common():
        print(f"   {nombre:>4}  {motif}")

    print("\nQuarantaine par source :")
    par_source = Counter(q["bien"]["source"] for q in resultats["quarantaine"])
    for source, nombre in par_source.most_common():
        print(f"   {source:<12} {nombre}")


if __name__ == "__main__":
    afficher(executer_pipeline(charger_tout()))
