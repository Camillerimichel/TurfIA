"""Score TurfIA — cf. L031.2, L031.1.

Le score global est une moyenne pondérée de sous-scores déjà normalisés sur [0, 100]
(cf. L031.2 §6). Les pondérations ne sont jamais codées en dur : elles sont fournies
par l'appelant (cf. ADR-002 de L006, table `parametre`).
"""

from __future__ import annotations

from src.core.constants import DECISIONS
from src.core.exceptions import ValidationError

# Pondérations par défaut, utilisables hors production (tests, exemples) — la valeur
# effective vient de la table `parametre` (cf. L026 §3.3).
PONDERATIONS_PAR_DEFAUT: dict[str, float] = {
    "marche": 1.0,
    "presse": 1.0,
    "forme": 1.0,
    "aptitude": 1.0,
    "professionnels": 1.0,
    "historique": 1.0,
    "value": 1.0,
    "contexte": 1.0,
}

SEUILS_DECISION_PAR_DEFAUT = (60.0, 75.0, 85.0)  # cf. L031.1 §9, paramétrables


def calculer_score(sous_scores: dict[str, float], poids: dict[str, float] | None = None) -> float:
    """Score TurfIA = Σ(SousScore_i × Poids_i) / Σ(Poids_i) (cf. L031.2 §6).

    Lève ValidationError si un sous-score est hors de [0, 100] ou si la somme des poids
    utilisés est nulle.
    """
    poids = poids or PONDERATIONS_PAR_DEFAUT
    for cle, valeur in sous_scores.items():
        if not 0 <= valeur <= 100:
            raise ValidationError(f"Sous-score '{cle}' hors de [0, 100] : {valeur}")

    poids_utilises = {cle: poids.get(cle, 0.0) for cle in sous_scores}
    somme_poids = sum(poids_utilises.values())
    if somme_poids == 0:
        raise ValidationError("La somme des poids utilisés est nulle.")

    return sum(sous_scores[cle] * poids_utilises[cle] for cle in sous_scores) / somme_poids


def determiner_decision(
    score_confiance: float,
    seuils: tuple[float, float, float] = SEUILS_DECISION_PAR_DEFAUT,
) -> str:
    """Traduit le score en décision (cf. L031.1 §9) : 4 niveaux définis par 3 seuils."""
    seuil_prudent, seuil_normal, seuil_opportunite = seuils
    if score_confiance < seuil_prudent:
        return DECISIONS[0]  # "Ne pas jouer"
    if score_confiance < seuil_normal:
        return DECISIONS[1]  # "Jeu prudent"
    if score_confiance < seuil_opportunite:
        return DECISIONS[2]  # "Jeu normal"
    return DECISIONS[3]  # "Forte opportunité"
