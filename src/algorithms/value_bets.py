"""Détection des Value Bets — cf. L031.5.

Un Value Bet est un cheval dont la probabilité estimée par TurfIA dépasse la
probabilité implicite du marché (cf. L029 Glossaire, L031.5 §1).
"""

from __future__ import annotations

from src.core.exceptions import ValidationError

SEUIL_SCORE_PAR_DEFAUT = 60.0
SEUIL_RISQUE_PAR_DEFAUT = 75.0


def calculer_valeur(p_turfia: float, p_marche: float) -> float:
    """Valeur = P_TurfIA - P_marché (cf. L031.5 §3)."""
    return p_turfia - p_marche


def calculer_ratio(p_turfia: float, p_marche: float) -> float:
    """Ratio = P_TurfIA / P_marché ; > 1 indique une sous-évaluation par le marché (cf. L031.5 §3)."""
    if p_marche <= 0:
        raise ValidationError("La probabilité de marché doit être strictement positive.")
    return p_turfia / p_marche


def est_value_bet(
    score_confiance: float,
    p_turfia: float,
    p_marche: float,
    risque: float,
    seuil_score: float = SEUIL_SCORE_PAR_DEFAUT,
    seuil_risque: float = SEUIL_RISQUE_PAR_DEFAUT,
) -> bool:
    """Critères d'éligibilité Value Bet (cf. L031.5 §4) : score suffisant, probabilité
    TurfIA supérieure à celle du marché, et risque sous le seuil maximal.
    """
    return score_confiance >= seuil_score and p_turfia > p_marche and risque <= seuil_risque


def interpreter_niveau_value(ratio: float) -> str:
    """Traduit le ratio en niveau de Value Bet (cf. L031.5 §5)."""
    if ratio < 1.00:
        return "Aucune valeur"
    if ratio <= 1.10:
        return "Faible"
    if ratio <= 1.25:
        return "Intéressante"
    return "Forte"
