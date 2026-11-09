from src.processing.traitement import nettoyer_bien

CHAMPS_NON_BLOQUANTS = ("chambres", "salles_bain")


def separer_biens(biens, regles, villes, regions, statuts):
    """Nettoie chaque bien, applique les règles et le range en propre ou en quarantaine.

    Renvoie (propres, quarantaine, avertissements, journal) :
    - propres : biens nettoyés sans règle bloquante violée ;
    - quarantaine : {"bien": bien brut, "motifs": [...]} ;
    - avertissements : (id_local, raison) pour chaque avertissement ;
    - journal : une entrée par bien reçu, utilisée par le rapport qualité.
    """
    propres, quarantaine, avertissements, journal = [], [], [], []

    for bien in biens:
        motifs = []
        avertissements_bien = []
        bien_nettoye, champs_corriges, erreurs_conversion = nettoyer_bien(
            bien, villes, regions, statuts
        )

        # Erreurs de conversion : bloquantes, sauf chambres et salles de bain
        for champ in erreurs_conversion:
            raison = f"{champ} illisible : {bien[champ]!r}"
            if champ in CHAMPS_NON_BLOQUANTS:
                avertissements_bien.append(raison)
            else:
                motifs.append(raison)

        # Règles appliquées au bien nettoyé, une seule fois chacune
        resultats = {regle.nom: regle.verifier(bien_nettoye) for regle in regles}
        for regle in regles:
            if resultats[regle.nom] != "violee":
                continue
            if regle.gravite == "avertissement":
                avertissements_bien.append(regle.nom)
            elif regle.champ not in erreurs_conversion:
                motifs.append(regle.motif)

        for raison in avertissements_bien:
            avertissements.append((bien["id_local"], raison))

        if motifs:
            quarantaine.append({"bien": bien, "motifs": motifs})
        else:
            propres.append(bien_nettoye)

        journal.append({
            "source": bien["source"],
            "id_local": bien["id_local"],
            "champs_corriges": champs_corriges,
            "erreurs_conversion": erreurs_conversion,
            "avertissements": avertissements_bien,
            "resultats": resultats,
            "en_quarantaine": bool(motifs),
        })

    return propres, quarantaine, avertissements, journal
