from datetime import date
from src.constantes import VALEURS_VIDES
from src.processing.traitement import convertir_prix, normaliser_type_bien, convertir_surface
from src.validation.validation import CATEGORIES

class RegleValidation:
    def __init__(self, nom, champ, motif, gravite, condition, obligatoire=False):
        self.nom = nom
        self.champ = champ
        self.motif = motif
        self.gravite = gravite
        self.obligatoire = obligatoire
        self.condition = condition

    def verifier(self, bien):
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
]
