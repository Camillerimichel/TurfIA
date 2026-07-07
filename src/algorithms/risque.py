"""Calcul du risque — cf. L031.3.

Le risque mesure l'incertitude de la course, indépendamment de la qualité des chevaux
(cf. L031.3 §1). Fonctions pures, pondérations fournies par l'appelant.
"""

from __future__ import annotations

from src.core.exceptions import ValidationError

PONDERATIONS_PAR_DEFAUT: dict[str, float] = {
    "marche": 1.0,
    "presse": 1.0,
    "course": 1.0,
    "terrain": 1.0,
    "historique": 1.0,
    "contexte": 1.0,
    "statistiques": 1.0,
}

SEUIL_REDUCTION_MISE_PAR_DEFAUT = 75.0  # cf. L031.3 §8, paramétrable


def calculer_risque(sous_risques: dict[str, float], poids: dict[str, float] | None = None) -> float:
    """Risque_global = Σ(SousRisque_i × Poids_i) / Σ(Poids_i) (cf. L031.3 §5)."""
    poids = poids or PONDERATIONS_PAR_DEFAUT
    for cle, valeur in sous_risques.items():
        if not 0 <= valeur <= 100:
            raise ValidationError(f"Sous-risque '{cle}' hors de [0, 100] : {valeur}")

    poids_utilises = {cle: poids.get(cle, 0.0) for cle in sous_risques}
    somme_poids = sum(poids_utilises.values())
    if somme_poids == 0:
        raise ValidationError("La somme des poids utilisés est nulle.")

    return sum(sous_risques[cle] * poids_utilises[cle] for cle in sous_risques) / somme_poids


def interpreter_risque(risque: float) -> str:
    """Traduit le risque en libellé (cf. L031.3 §6)."""
    if risque <= 25:
        return "Très faible"
    if risque <= 50:
        return "Faible"
    if risque <= 75:
        return "Moyen"
    return "Élevé"


def ajuster_budget_selon_risque(
    budget: float,
    risque: float,
    seuil_reduction: float = SEUIL_REDUCTION_MISE_PAR_DEFAUT,
    facteur_reduction: float = 0.5,
) -> float:
    """Réduit le budget recommandé si le risque dépasse le seuil (cf. L031.3 §8).

    Ne modifie jamais le classement des chevaux, uniquement le montant proposé.
    """
    if risque > seuil_reduction:
        return round(budget * facteur_reduction, 2)
    return budget
