from src.constantes import VALEURS_VIDES
from src.processing.traitement import convertir_prix, normaliser_type_bien
from src.validation.validation import CATEGORIES

class RegleValidation:
    def __init__(self, nom, champ, motif, condition):
        self.nom = nom
        self.champ = champ
        self.motif = motif
        self.condition = condition

    def verifier(self, bien):
        valeur = bien.get(self.champ)
        if valeur in VALEURS_VIDES:
            return "non_evaluable"

        resultat = self.condition(valeur)

        return "respectee" if resultat else "violee"


def _prix_est_positif(valeur):
    prix = convertir_prix(valeur)
    if prix is None:
        return False
    return prix > 0


def _type_bien_est_reconnu(valeur):
    return normaliser_type_bien(valeur) in CATEGORIES


def _transaction_est_valide(valeur):
    return valeur in ("vente", "location")


prix_positif = RegleValidation(
    "prix_positif", "prix", "Le prix doit être supérieur à zéro", _prix_est_positif
)
type_bien_reconnu = RegleValidation(
    "type_bien_reconnu",
    "type_bien",
    "Le type de bien doit appartenir aux catégories reconnues",
    _type_bien_est_reconnu,
)
transaction_valide = RegleValidation(
    "transaction_valide",
    "type_transaction",
    "La transaction doit être une vente ou une location",
    _transaction_est_valide,
)

REGLES = [prix_positif, type_bien_reconnu, transaction_valide]
        