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

# Répartition du budget entre types de pari constructibles (cf. L031.6 §5-6) :
# poids plus élevé pour les types à taux de réussite plus fréquent (Simple Placé,
# 2 sur 4) qu'aux types plus rares mais mieux rémunérés (Couplé Gagnant) — choix
# assumé d'optimiser les gains fréquents plutôt que les gros gains rares.
REPARTITION_BUDGET_PAR_DEFAUT: dict[str, float] = {
    "Simple Placé": 0.35,
    "2 sur 4": 0.25,
    "Simple Gagnant": 0.20,
    "Couplé Placé": 0.15,
    "Couplé Gagnant": 0.05,
}


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


def categoriser(
    partant: PartantClasse, seuil_base: float = 85.0, seuil_chance_reguliere: float = 70.0, rangs_base_max: int = 2
) -> str:
    """Catégorisation fonctionnelle (cf. L031.6 §4) — heuristique basée sur le rang,
    le score final et le risque. Retourne une valeur de CATEGORIES_SELECTION.

    `rangs_base_max` autorise plusieurs partants en tête de classement à devenir
    « Base » (pas seulement le n°1) — nécessaire pour construire les paris
    combinés « Base n°1 + Base n°2 » (Couplé Gagnant, 2 sur 4, cf. L031.6 §5).
    """
    if partant.rang is not None and partant.rang <= rangs_base_max and partant.score_final >= seuil_base:
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


def construire_paris(
    partants_classes: list[PartantClasse],
    budget: float,
    repartition: dict[str, float] = REPARTITION_BUDGET_PAR_DEFAUT,
) -> list[tuple[str, list[PartantClasse], float]]:
    """Construit les paris à partir des catégories déjà assignées par `categoriser`
    (cf. L031.6 §5) : Simple Gagnant (Base n°1), Simple Placé (Base n°1 et/ou
    Chance régulière n°1, un pari distinct chacun), Couplé Gagnant (Base n°1 +
    Base n°2), Couplé Placé (Base n°1 + Chance régulière n°1), 2 sur 4 (deux
    Bases + deux Chances régulières). Quinté Flexi n'est volontairement pas
    construit ici (cf. plan, complexité disproportionnée).

    `budget` est réparti entre les types réellement constructibles au prorata de
    `repartition` (cf. L031.6 §6) : un type non constructible (catégories
    insuffisantes) redistribue sa part aux autres, le budget conseillé est donc
    toujours intégralement utilisé. Retourne une liste de
    `(type_pari, chevaux_impliqués, mise)`.
    """
    if budget <= 0:
        return []

    bases = [p for p in partants_classes if p.categorie == "Base"]
    chances = [p for p in partants_classes if p.categorie == "Chance régulière"]

    groupes: dict[str, list[list[PartantClasse]]] = {}
    if bases:
        groupes["Simple Gagnant"] = [[bases[0]]]
    simple_place = [[bases[0]]] if bases else []
    if chances:
        simple_place.append([chances[0]])
    if simple_place:
        groupes["Simple Placé"] = simple_place
    if len(bases) >= 2:
        groupes["Couplé Gagnant"] = [[bases[0], bases[1]]]
    if bases and chances:
        groupes["Couplé Placé"] = [[bases[0], chances[0]]]
    if len(bases) >= 2 and len(chances) >= 2:
        groupes["2 sur 4"] = [[bases[0], bases[1], chances[0], chances[1]]]

    poids_total = sum(repartition[type_pari] for type_pari in groupes)
    if poids_total == 0:
        return []

    paris: list[tuple[str, list[PartantClasse], float]] = []
    for type_pari, combinaisons in groupes.items():
        part_type = budget * (repartition[type_pari] / poids_total)
        mise_par_pari = round(part_type / len(combinaisons), 2)
        for chevaux in combinaisons:
            paris.append((type_pari, chevaux, mise_par_pari))
    return paris
