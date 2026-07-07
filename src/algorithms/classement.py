"""Classement final et construction des paris — cf. L031.6.

Dernière étape avant la génération des recommandations : transforme les scores
calculés en classement, catégories fonctionnelles et budget conseillé.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.core.constants import CATEGORIES_SELECTION
from src.core.exceptions import BusinessRuleError

BONUS_VALUE_BET_PAR_DEFAUT = 5.0
MALUS_RISQUE_PAR_DEFAUT = 0.2  # appliqué à `risque` avant soustraction (cf. L031.6 §3)

# Paliers de budget par score de confiance (cf. L031.6 §6, paramétrables)
PALIERS_BUDGET_PAR_DEFAUT: tuple[tuple[float, float], ...] = (
    (60.0, 0.0),
    (75.0, 10.0),
    (85.0, 25.0),
)
BUDGET_MAXIMAL_PAR_DEFAUT = 50.0


@dataclass
class PartantClasse:
    partant_id: int
    score_turfia: float
    score_final: float
    risque: float
    roi_theorique: float
    consensus: float
    evolution_cote: float
    value_bet: bool
    rang: int | None = None
    categorie: str | None = None


def calculer_score_final(
    score_turfia: float,
    value_bet: bool,
    risque: float,
    bonus_value_bet: float = BONUS_VALUE_BET_PAR_DEFAUT,
    malus_risque: float = MALUS_RISQUE_PAR_DEFAUT,
) -> float:
    """Score Final = Score TurfIA + Bonus Value Bet - Malus Risque (cf. L031.6 §3)."""
    bonus = bonus_value_bet if value_bet else 0.0
    return score_turfia + bonus - (risque * malus_risque)


def trier_partants(partants: list[PartantClasse]) -> list[PartantClasse]:
    """Trie par score final décroissant, avec départages successifs (cf. L031.6 §3) :
    meilleur Score TurfIA, meilleur ROI théorique, meilleur consensus, meilleure
    évolution des cotes. Assigne le rang (1 = meilleur).
    """
    classes = sorted(
        partants,
        key=lambda p: (-p.score_final, -p.score_turfia, -p.roi_theorique, -p.consensus, -p.evolution_cote),
    )
    for rang, partant in enumerate(classes, start=1):
        partant.rang = rang
    return classes


def categoriser(partant: PartantClasse, seuil_base: float = 85.0, seuil_chance_reguliere: float = 70.0) -> str:
    """Catégorisation fonctionnelle (cf. L031.6 §4) — heuristique basée sur le rang,
    le score final et le risque. Retourne une valeur de CATEGORIES_SELECTION.
    """
    if partant.rang == 1 and partant.score_final >= seuil_base:
        categorie = CATEGORIES_SELECTION[0]  # "Base"
    elif partant.score_final >= seuil_chance_reguliere:
        categorie = CATEGORIES_SELECTION[1]  # "Chance régulière"
    elif partant.value_bet:
        categorie = CATEGORIES_SELECTION[2]  # "Outsider"
    elif partant.score_final >= 40:
        categorie = CATEGORIES_SELECTION[3]  # "Tocard"
    else:
        categorie = CATEGORIES_SELECTION[4]  # "Écarté"
    partant.categorie = categorie
    return categorie


def calculer_budget(
    score_confiance: float,
    paliers: tuple[tuple[float, float], ...] = PALIERS_BUDGET_PAR_DEFAUT,
    budget_maximal: float = BUDGET_MAXIMAL_PAR_DEFAUT,
) -> float:
    """Budget conseillé selon le score de confiance de la course (cf. L031.6 §6)."""
    for seuil, budget in paliers:
        if score_confiance < seuil:
            return budget
    return budget_maximal


def verifier_absence_martingale(budget_propose: float, budget_precedent: float, perte_precedente: bool) -> None:
    """Garde-fou : aucune augmentation de mise n'est autorisée après une perte
    (cf. L031.6 §6, interdiction explicite de toute logique de martingale).
    """
    if perte_precedente and budget_propose > budget_precedent:
        raise BusinessRuleError(
            "Augmentation de budget après une perte refusée (interdiction de martingale, cf. L031.6 §6)."
        )
