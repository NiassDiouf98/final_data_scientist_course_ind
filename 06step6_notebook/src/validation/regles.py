from datetime import date
from src.constantes import VALEURS_VIDES
from src.processing.traitement import convertir_prix, normaliser_type_bien, convertir_surface
from src.validation.validation import CATEGORIES

LOYER_MIN, LOYER_MAX = 25_000, 5_000_000
CHAMBRES_MAX_PETIT_LOGEMENT = 10
SALLES_BAIN_MARGE = 2
TYPES_SANS_CHAMBRES = {"Local commercial", "Terrain"}


class RegleValidation:
    def __init__(
        self, nom, champ, motif, gravite, condition, obligatoire=False,
        applicable=None,
    ):
        self.nom = nom
        self.champ = champ
        self.motif = motif
        self.gravite = gravite
        self.obligatoire = obligatoire
        self.condition = condition
        self.applicable = applicable

    def verifier(self, bien):
        if self.applicable is not None and not self.applicable(bien):
            return "non_evaluable"

        valeur = bien.get(self.champ)
        if valeur in VALEURS_VIDES:
            return "violee" if self.obligatoire else "non_evaluable"

        resultat = self.condition(bien)

        return "respectee" if resultat else "violee"


def _prix_est_positif(bien):
    prix = convertir_prix(bien.get("prix"))
    if prix is None:
        return False
    return prix > 0


def _type_bien_est_reconnu(bien):
    return normaliser_type_bien(bien.get("type_bien")) in CATEGORIES


def _transaction_est_valide(bien):
    return bien.get("type_transaction") in ("vente", "location")


def _id_est_present(bien):
    valeur = bien.get("id_local")
    return (
        valeur not in VALEURS_VIDES
        and bool(str(valeur).strip())
    )


def _surface_est_positive(bien):
    surface = convertir_surface(bien.get("surface"))
    return surface is not None and surface > 0


def _date_est_valide(bien):
    try:
        date.fromisoformat(str(bien.get("date")))
        return True
    except (TypeError, ValueError):
        return False


def _prix_dans_la_norme(bien):
    prix = convertir_prix(bien.get("prix"))
    return prix is not None and 100_000 <= prix <= 2_000_000_000


def _surface_dans_la_norme(bien):
    surface = convertir_surface(bien.get("surface"))
    return surface is not None and 5 <= surface <= 2_000


def _date_non_future_si_vendu(bien):
    if bien.get("statut") not in {"Vendu", "Vente conclue", "Acte signé"}:
        return True
    valeur_date = bien.get("date")
    return valeur_date <= date.today().isoformat()


def _est_location(bien):
    return bien.get("type_transaction") == "location"


def _est_vente(bien):
    return bien.get("type_transaction") == "vente"


def _loyer_dans_la_norme(bien):
    loyer = convertir_prix(bien.get("prix"))
    return loyer is not None and LOYER_MIN <= loyer <= LOYER_MAX


def _est_appartement_ou_studio(bien):
    type_bien = normaliser_type_bien(bien.get("type_bien"))
    return str(type_bien).strip().lower() in {"appartement", "studio"}


def _salles_bain_comparables(bien):
    type_bien = normaliser_type_bien(bien.get("type_bien"))
    chambres = bien.get("chambres")
    return (
        type_bien not in TYPES_SANS_CHAMBRES
        and chambres not in VALEURS_VIDES
    )


def _chambres_dans_la_norme(bien):
    try:
        return float(bien.get("chambres")) <= CHAMBRES_MAX_PETIT_LOGEMENT
    except (TypeError, ValueError):
        return False


def _salles_bain_dans_la_norme(bien):
    chambres = float(bien.get("chambres"))
    salles_bain = float(bien.get("salles_bain"))
    return salles_bain <= chambres + SALLES_BAIN_MARGE


def creer_regle_ville_region(referentiel):
    def _ville_coherente(bien):
        ville = bien.get("ville")
        region = bien.get("region")
        return ville in referentiel and referentiel[ville] == region

    return RegleValidation(
        "ville_region_coherentes",
        "ville",
        "Ville inconnue du référentiel ou incompatible avec la région",
        "avertissement",
        _ville_coherente,
    )


def creer_regle_prix_m2_hors_fourchette(referentiel):
    """referentiel : {categorie: (prix_m2_min, prix_m2_max)}, voir charger_referentiel_prix_m2."""

    def _prix_m2_calculable(bien):
        # Ventes seulement (périodicité des loyers inconnue),
        # avec une catégorie connue, un prix et une surface utilisables
        if not _est_vente(bien):
            return False
        if normaliser_type_bien(bien.get("type_bien")) not in referentiel:
            return False
        prix = convertir_prix(bien.get("prix"))
        surface = convertir_surface(bien.get("surface"))
        return prix is not None and surface is not None and surface > 0

    def _prix_m2_dans_la_fourchette(bien):
        minimum, maximum = referentiel[normaliser_type_bien(bien.get("type_bien"))]
        prix_m2 = convertir_prix(bien.get("prix")) / convertir_surface(bien.get("surface"))
        return minimum <= prix_m2 <= maximum

    return RegleValidation(
        "prix_m2_hors_fourchette",
        "prix",
        "Le prix au m² est hors de la fourchette indicative de la catégorie",
        "avertissement",
        _prix_m2_dans_la_fourchette,
        applicable=_prix_m2_calculable,
    )


prix_positif = RegleValidation(
    "prix_positif",
    "prix",
    "Le prix doit être présent et supérieur à zéro",
    "bloquante",
    _prix_est_positif,
    obligatoire=True,
)
type_bien_reconnu = RegleValidation(
    "type_bien_reconnu",
    "type_bien",
    "Le type de bien doit appartenir aux catégories reconnues",
    "bloquante",
    _type_bien_est_reconnu,
)
transaction_valide = RegleValidation(
    "transaction_valide",
    "type_transaction",
    "La transaction doit être une vente ou une location",
    "bloquante",
    _transaction_est_valide,
    obligatoire=True,
)
id_present = RegleValidation(
    "id_present",
    "id_local",
    "L'identifiant du bien est obligatoire",
    "bloquante",
    _id_est_present,
    obligatoire=True,
)
surface_positive = RegleValidation(
    "surface_positive",
    "surface",
    "La surface doit être présente et supérieure à zéro",
    "bloquante",
    _surface_est_positive,
    obligatoire=True,
)
date_valide = RegleValidation(
    "date_valide",
    "date",
    "La date doit être une date valide au format ISO",
    "bloquante",
    _date_est_valide,
    obligatoire=True,
)
prix_atypique = RegleValidation(
    "prix_atypique",
    "prix",
    "Le prix est inhabituellement bas ou élevé",
    "avertissement",
    _prix_dans_la_norme,
    applicable=_est_vente
)
surface_atypique = RegleValidation(
    "surface_atypique",
    "surface",
    "La surface est inhabituellement petite ou grande",
    "avertissement",
    _surface_dans_la_norme,
)
date_non_future_si_vendu = RegleValidation(
    "date_non_future_si_vendu",
    "date",
    "La date d'un bien vendu ne peut pas être dans le futur",
    "bloquante",
    _date_non_future_si_vendu,
)
loyer_atypique = RegleValidation(
    "loyer_atypique",
    "prix",
    "Le loyer mensuel est hors de la fourchette habituelle",
    "avertissement",
    _loyer_dans_la_norme,
    applicable=_est_location,
)
chambres_atypiques = RegleValidation(
    "chambres_atypiques",
    "chambres",
    "Un appartement ou studio dépasse 10 chambres, à vérifier",
    "avertissement",
    _chambres_dans_la_norme,
    applicable=_est_appartement_ou_studio,
)
salles_bain_atypiques = RegleValidation(
    "salles_bain_atypiques",
    "salles_bain",
    "Le nombre de salles de bain dépasse celui des chambres de plus de 2",
    "avertissement",
    _salles_bain_dans_la_norme,
    applicable=_salles_bain_comparables,
)

REGLES = [
    prix_positif,
    type_bien_reconnu,
    transaction_valide,
    id_present,
    surface_positive,
    date_valide,
    prix_atypique,
    surface_atypique,
    date_non_future_si_vendu,
    loyer_atypique,
    chambres_atypiques,
    salles_bain_atypiques,
]
