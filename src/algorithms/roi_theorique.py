"""Calcul du ROI théorique — cf. L031.4.

Compare la probabilité TurfIA à la probabilité implicite du marché pour estimer la
rentabilité attendue d'un pari avant le départ.
"""

from __future__ import annotations

from src.core.exceptions import ValidationError


def probabilites_implicites_normalisees(cotes: list[float]) -> list[float]:
    """Probabilités implicites du marché, marge de l'opérateur neutralisée (cf. L031.4 §3).

    La probabilité brute d'une cote décimale est `1 / cote` ; la somme de ces
    probabilités sur l'ensemble d'une course dépasse toujours 100 % (marge de
    l'opérateur). On neutralise cette marge en renormalisant pour que la somme
    des probabilités du champ vaille exactement 1.
    """
    if not cotes:
        return []
    if any(c <= 0 for c in cotes):
        raise ValidationError("Une cote doit être strictement positive.")

    brutes = [1.0 / c for c in cotes]
    somme = sum(brutes)
    return [p / somme for p in brutes]


def probabilite_turfia(score_cheval: float, somme_scores: float) -> float:
    """Probabilité TurfIA = score du cheval / somme des scores du champ (cf. L031.4 §4)."""
    if somme_scores <= 0:
        raise ValidationError("La somme des scores du champ doit être strictement positive.")
    return score_cheval / somme_scores


def esperance(probabilite_turfia: float, rapport_estime: float, mise: float) -> float:
    """Espérance = P_TurfIA × Rapport_estimé - Mise (cf. L031.4 §5)."""
    return probabilite_turfia * rapport_estime - mise


def roi_theorique(esperance_pari: float, mise: float) -> float:
    """ROI théorique = (Espérance / Mise) × 100 (cf. L031.4 §6)."""
    if mise <= 0:
        raise ValidationError("La mise doit être strictement positive pour calculer un ROI.")
    return (esperance_pari / mise) * 100


def interpreter_roi(roi: float) -> str:
    """Traduit le ROI théorique en libellé (cf. L031.4 §9)."""
    if roi < 0:
        return "À éviter"
    if roi <= 10:
        return "Faible intérêt"
    if roi <= 25:
        return "Intéressant"
    return "Très favorable"
