import pandas as pd
import numpy as np

def vers_dataframe(biens):
    """Liste de biens (dictionnaires) -> DataFrame, une ligne par bien, une colonne par champ."""
    return pd.DataFrame(biens)


def separer_transactions(df):
    """Renvoie (ventes, locations) : deux DataFrames."""
    ventes = df[df["type_transaction"] == "vente"].copy()
    locations = df[df["type_transaction"] == "location"].copy()
    return ventes, locations


def resumer(valeurs):
    """Statistiques descriptives d'une suite de nombres, en ignorant les valeurs manquantes.
    Renvoie un dict : nombre, moyenne, mediane, ecart_type, minimum, q1, q3, maximum."""
    valeurs = np.asarray(valeurs, dtype=float)
    valeurs = valeurs[~np.isnan(valeurs)]
    if len(valeurs) == 0:
        return {
            "nombre": 0,
            "moyenne": None,
            "mediane": None,
            "ecart_type": None,
            "minimum": None,
            "q1": None,
            "q3": None,
            "maximum": None
        }
    return {
        "nombre": len(valeurs),
        "moyenne": np.mean(valeurs),
        "mediane": np.median(valeurs),
        "ecart_type": np.std(valeurs, ddof=1),
        "minimum": np.min(valeurs),
        "q1": np.percentile(valeurs, 25),
        "q3": np.percentile(valeurs, 75),
        "maximum": np.max(valeurs)
    }


def statistiques_descriptives(df, colonnes=("prix", "surface")):
    """Renvoie {colonne: resumer(df[colonne])} pour chaque colonne."""
    return {colonne: resumer(df[colonne]) for colonne in colonnes}


def ajouter_prix_m2(df):
    """Renvoie une copie de df avec une colonne prix_m2 = prix / surface,
    ou NaN quand le calcul n'a pas de sens."""
    resultat = df.copy()
    resultat["prix_m2"] = np.where(
        resultat["surface"] > 0,
        resultat["prix"] / resultat["surface"],
        np.nan
    )
    return resultat


def resultats_par_groupe(df, colonne_groupe, colonne_valeur):
    """Pour chaque valeur de colonne_groupe : nombre, moyenne et médiane de colonne_valeur.
    Renvoie un DataFrame trié par médiane décroissante."""
    return df.groupby(colonne_groupe)[colonne_valeur].agg(nombre="count", moyenne="mean", mediane="median").sort_values("mediane", ascending=False)