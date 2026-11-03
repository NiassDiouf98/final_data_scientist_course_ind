from src.processing.traitement import cle_rapprochement


def detecter_doublons(biens):
    """Sépare les biens uniques, et signale les doublons exacts, les conflits
    et les doublons probables. Aucun bien n'est perdu : chacun finit soit dans
    biens_uniques, soit dans conflits."""
    
    # grouper par identité (source, id_local)
    groupes_identifiants = {}
    for bien in biens:
        cle = (bien.get("source"), bien.get("id_local"))
        groupes_identifiants.setdefault(cle, []).append(bien)

    biens_uniques = []
    doublons_exacts = []
    conflits = []
    biens_a_rapprocher = []

    for groupe in groupes_identifiants.values():
        if len(groupe) == 1:
            biens_a_rapprocher.append(groupe[0])
        elif all(bien == groupe[0] for bien in groupe[1:]):
            doublons_exacts.append(groupe)
            biens_a_rapprocher.append(groupe[0])
        else:
            conflits.append(groupe)

    # grouper les biens qui continuent par cle_rapprochement(bien)
    groupes_rapprochement = {}
    for bien in biens_a_rapprocher:
        cle = cle_rapprochement(bien)
        groupes_rapprochement.setdefault(cle, []).append(bien)

    doublons_probables = []
    for groupe in groupes_rapprochement.values():
        biens_uniques.extend(groupe)
        if len(groupe) > 1:
            doublons_probables.append(groupe)

    
    return biens_uniques, doublons_exacts, conflits, doublons_probables