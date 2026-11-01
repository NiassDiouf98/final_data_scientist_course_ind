from src.loaders.harmonisation import charger_notaires, charger_agences, charger_historique, charger_particuliers, charger_plateforme
from src.validation.inventaire import inventorier

sources = {
    'notaires': charger_notaires,
    'agence': charger_agences,
    'historique': charger_historique,
    'particuliers': charger_particuliers,
    'plateforme': charger_plateforme
}


if __name__ == "__main__":
    for nom, chargeur in sources.items():
        data = chargeur()
        inv = inventorier(data)
        print(f"\n=== {nom.upper()} ===\n{inv}\n")