from src.loaders.harmonisation import charger_notaires, charger_historique, charger_plateforme, charger_particuliers, charger_agences


def test_charger_notaires():
    notaires = charger_notaires()

    assert len(notaires) == 410

    attendu = {"source": "notaires","id_local": "NOT-02192","type_bien": "Villa","region": "Sédhiou","ville": "Bounkiling","date": "2019-05-09","prix": "320860000.0","surface": "392.1","chambres": "3","salles_bain": None,"type_transaction": "vente","periodicite": None,"statut": "Vendu"}

    assert notaires[0] == attendu


def test_charger_historique():
    historique = charger_historique()

    assert len(historique) == 528

    attendu = {"source": "historique","id_local": "HIS-0001","type_bien": "Studio","region": "Louga","ville": "Linguère","date": "2019-11-19","prix": "26 620 000","surface": "44.7","chambres": "2","salles_bain": "1","type_transaction": "vente","periodicite": None,"statut": None}

    assert historique[0] == attendu


def test_charger_plateforme():
    plateforme = charger_plateforme()

    assert len(plateforme) == 875

    attendu = {"source": "plateforme","id_local": "PLT-00002","type_bien": "Maison","region": "Kolda","ville": "Kolda","date": "2022-09-15","prix": "57.62 millions","surface": "89.6","chambres": "5","salles_bain": "3","type_transaction": "vente","periodicite": None,"statut": "Vendu"}
    attendu_location = {"source": "plateforme","id_local": "PLT-00399","type_bien": "Appartement","region": "Sédhiou","ville": "Bounkiling","date": "2021-01-25","prix": "380000","surface": "136.8","chambres": "3","salles_bain": "1","type_transaction": "location","periodicite": "mensuel","statut": "Loué"}

    assert plateforme[1] == attendu
    assert plateforme[398] == attendu_location


def test_charger_particuliers():
    particuliers = charger_particuliers()

    assert len(particuliers) == 731

    attendu = {'source': 'particuliers', 'id_local': 'PRT-01461', 'type_bien': 'Studio', 'region': 'Fatick', 'ville': 'Gossas',
                'date': '11/05/2022', 'prix': 18152000, 'surface': 50.0, 'chambres': 4, 'salles_bain': 4,
                'type_transaction': 'vente', 'periodicite': None, 'statut': 'En vente'}

    assert particuliers[0] == attendu


def test_charger_agences():
    agences = charger_agences()

    assert len(agences) == 640

    attendu = {'source': 'agence', 'id_local': 'AGT-00821', 'date': '02/12/2023', 'region': 'Fatick', 'ville': 'Fatick', 'type_bien': 'Studio', 'prix': 38448000, 'surface': 35.7, 'chambres': 3, 'salles_bain': 4, 'type_transaction': 'vente', 'periodicite': None, 'statut': 'Vendu'}
    attendu_location = {'source': 'agence', 'id_local': 'AGT-00834', 'date': '2021-11-30', 'region': 'Dakar', 'ville': 'Pikine', 'type_bien': 'Terrain', 'prix': 360000, 'surface': 1336.5, 'chambres': 0, 'salles_bain': 0, 'type_transaction': 'location', 'periodicite': None, 'statut': 'Loué'}

    assert agences[0] == attendu
    location = next(b for b in agences if b["id_local"] == "AGT-00834")
    assert location == attendu_location