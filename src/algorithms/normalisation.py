"""Normalisation des indicateurs — cf. L031.2 §4.

Fonctions pures : aucune donnée n'est lue ou écrite, tout est fourni en paramètre
(cf. L006 §4.2, L015 §8.3).
"""

from __future__ import annotations

from src.core.constants import SCORE_MAX, SCORE_MIN


def normaliser(valeur: float, minimum: float, maximum: float, inverse: bool = False) -> float:
    """Convertit `valeur` sur l'échelle [0, 100] (cf. L031.2 §4).

    Si `inverse` est vrai, une valeur basse est considérée favorable
    (`Score = 100 - Score_normalisé`, cf. L031.2 §4).
    Si `maximum == minimum`, retourne une valeur neutre (50.0) plutôt que de diviser par zéro.
    """
    if maximum == minimum:
        return 50.0

    score = SCORE_MAX * (valeur - minimum) / (maximum - minimum)
    score = max(SCORE_MIN, min(SCORE_MAX, score))
    return (SCORE_MAX - score) if inverse else score
