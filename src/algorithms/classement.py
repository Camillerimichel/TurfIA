"""Classement final et construction des paris — cf. L031.6.

Dernière étape avant la génération des recommandations : transforme les scores
calculés en classement, catégories fonctionnelles et budget conseillé.
"""

from __future__ import annotations

import math
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
# 2 sur 4) qu'aux types plus rares mais mieux rémunérés (Couplé Gagnant, Quinté
# Flexi) — choix assumé d'optimiser les gains fréquents plutôt que les gros
# gains rares. Quinté Flexi reçoit la plus petite part (variance la plus forte
# de tous les types), prélevée sur Simple Placé.
REPARTITION_BUDGET_PAR_DEFAUT: dict[str, float] = {
    "Simple Placé": 0.30,
    "2 sur 4": 0.25,
    "Simple Gagnant": 0.20,
    "Couplé Placé": 0.15,
    "Couplé Gagnant": 0.05,
    "Quinté Flexi": 0.05,
}

# Vérifié réellement le 2026-07-08 (champ `valeursFlexiAutorisees` des pools PMU
# QUINTE_PLUS) : le Flexi permet de payer 100/50/25 % du prix plein d'un ticket
# Quinté+ (et de toucher la même fraction du dividende si gagnant) — pas de
# valeur intermédiaire. Mise de base réelle d'un ticket Quinté+ : 2 €.
VALEURS_FLEXI_AUTORISEES: tuple[int, ...] = (100, 50, 25)
MISE_BASE_QUINTE = 2.0


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
    """Score Final = Score TurfIA + Bonus Value Bet - Malus Risque (cf. L031.6 §3).

    Borné à [0, 100] : le SAD ne le précise pas explicitement, mais
    `analyses.score_confiance` (`ck_analyse_score`) et tous les seuils qui en
    dépendent (`determiner_decision`, `calculer_budget`) présupposent une
    échelle 0-100. Sans borne, un Score TurfIA déjà élevé + Bonus Value Bet
    peut dépasser 100 (vérifié réellement le 2026-07-11 : score_turfia=100,
    value_bet=True, risque=18.75 -> 100 + 5 - 3.75 = 101.25), violant la
    contrainte SQL et faisant échouer l'analyse (et, en cascade, toute la
    course dans `AutomatisationService.analyser_courses_du_jour` — cf.
    PROJECT_STATE.md).
    """
    bonus = bonus_value_bet if value_bet else 0.0
    return max(0.0, min(100.0, score_turfia + bonus - (risque * malus_risque)))


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


def _construire_selection_quinte(partants_classes: list[PartantClasse]) -> list[PartantClasse]:
    """Sélection Quinté Flexi (cf. L031.6 §5, littéral) : Bases + Chances
    régulières + Outsider principal + Tocard éventuel — ce dernier seulement si
    son ROI théorique propre reste positif (« Tocard éventuel si le ROI attendu
    reste positif »).
    """
    bases = [p for p in partants_classes if p.categorie == "Base"]
    chances = [p for p in partants_classes if p.categorie == "Chance régulière"]
    outsiders = [p for p in partants_classes if p.categorie == "Outsider"]
    tocards = [p for p in partants_classes if p.categorie == "Tocard"]

    selection = [*bases, *chances]
    if outsiders:
        selection.append(outsiders[0])
    if tocards and tocards[0].roi_theorique > 0:
        selection.append(tocards[0])
    return selection


def _calculer_mise_quinte_flexi(nb_chevaux: int, budget_alloue: float) -> float | None:
    """Coût le plus élevé possible parmi les paliers Flexi réels (100/50/25 %,
    cf. vérification réelle du 2026-07-08) qui tient dans `budget_alloue` : le
    Quinté+ joue automatiquement toutes les combinaisons de 5 chevaux parmi les
    `nb_chevaux` sélectionnés (C(nb_chevaux, 5)), au tarif Flexi choisi.
    Retourne `None` si même le palier le plus bas (25 %) dépasse le budget
    alloué (champ trop large compte tenu du budget disponible).
    """
    nb_combinaisons = math.comb(nb_chevaux, 5)
    for pourcentage in VALEURS_FLEXI_AUTORISEES:
        cout = MISE_BASE_QUINTE * nb_combinaisons * (pourcentage / 100)
        if cout <= budget_alloue:
            return round(cout, 2)
    return None


def construire_paris(
    partants_classes: list[PartantClasse],
    budget: float,
    repartition: dict[str, float] = REPARTITION_BUDGET_PAR_DEFAUT,
    quinte: bool = True,
) -> list[tuple[str, list[PartantClasse], float]]:
    """Construit les paris à partir des catégories déjà assignées par `categoriser`
    (cf. L031.6 §5) : Simple Gagnant (Base n°1), Simple Placé (Base n°1 et/ou
    Chance régulière n°1, un pari distinct chacun), Couplé Gagnant (Base n°1 +
    Base n°2), Couplé Placé (Base n°1 + Chance régulière n°1), 2 sur 4 (deux
    Bases + deux Chances régulières), Quinté Flexi (Bases + Chances régulières +
    Outsider principal + Tocard éventuel, cf. `_construire_selection_quinte`).

    `quinte` (retour utilisateur, 2026-07-13 : « structure de paris spécifique
    sur les Quintés ») gate ces 4 derniers types : vérifié réellement le
    2026-07-08 contre une vraie course Quinté+ arrivée, le PMU n'expose Couplé
    Gagnant/Placé, 2 sur 4 et Quinté Flexi que sur les courses Quinté+ (une
    course ordinaire n'expose que `COUPLE_ORDRE`, à ordre exigé, un pari
    différent) — un pari de ces 4 types construit sur une course ordinaire ne
    trouve donc jamais de rapport PMU correspondant (`ControleRoiService` le
    journalise et l'ignore). `quinte=False` (course ordinaire) ne construit
    donc que Simple Gagnant/Placé ; `quinte=True` (défaut, courses Quinté+
    réelles, et rétrocompatible avec les appels existants qui ne précisent pas
    ce paramètre) conserve le répertoire complet.

    `budget` est réparti entre les types réellement constructibles au prorata de
    `repartition` (cf. L031.6 §6) : un type non constructible (catégories
    insuffisantes, ou exclu par `quinte=False`) redistribue sa part aux autres,
    le budget conseillé est donc toujours intégralement utilisé — sauf Quinté
    Flexi, dont le coût est quantifié par palier Flexi (100/50/25 %) plutôt
    que librement divisible : si même 25 % dépasse sa part allouée, il est
    simplement omis (sa part reste non engagée, cas rare). Retourne une liste
    de `(type_pari, chevaux_impliqués, mise)`.
    """
    if budget <= 0 or not partants_classes:
        return []

    bases = [p for p in partants_classes if p.categorie == "Base"]
    chances = [p for p in partants_classes if p.categorie == "Chance régulière"]

    # Le budget est engagé dès que la décision n'est pas "Ne pas jouer" (score de
    # confiance de la course = score final de la tête de liste, cf. L031.1 §9,
    # `AnalyseService.analyser_course`). Les seuils de `categoriser` (Base/Chance
    # régulière) sont indépendants des paliers de budget (cf. L031.6 §4, critères
    # qualitatifs non chiffrés dans le SAD) : la tête de liste peut donc engager
    # un budget sans elle-même atteindre Base ni Chance régulière — auparavant
    # aucun pari n'était alors proposé pour dépenser ce budget (vérifié
    # réellement en base : 2 analyses "Jeu prudent"/10 €, 0 pari créé). Filet de
    # sécurité : Simple Placé sur la tête de liste, jamais Simple Gagnant
    # (réservé à une vraie Base, cf. L031.6 §5) ; sa catégorie affichée reste
    # inchangée (ex. "Tocard"), seule la construction du pari en tient compte.
    tete_de_liste = partants_classes[0]
    secours_tete_de_liste = not bases and not chances

    groupes: dict[str, list[list[PartantClasse]]] = {}
    if bases:
        groupes["Simple Gagnant"] = [[bases[0]]]
    simple_place = [[bases[0]]] if bases else []
    if chances:
        simple_place.append([chances[0]])
    if not simple_place and secours_tete_de_liste:
        simple_place = [[tete_de_liste]]
    if simple_place:
        groupes["Simple Placé"] = simple_place
    if quinte:
        if len(bases) >= 2:
            groupes["Couplé Gagnant"] = [[bases[0], bases[1]]]
        if bases and chances:
            groupes["Couplé Placé"] = [[bases[0], chances[0]]]
        if len(bases) >= 2 and len(chances) >= 2:
            groupes["2 sur 4"] = [[bases[0], bases[1], chances[0], chances[1]]]
        selection_quinte = _construire_selection_quinte(partants_classes)
        if len(selection_quinte) >= 5:
            groupes["Quinté Flexi"] = [selection_quinte]

    poids_total = sum(repartition[type_pari] for type_pari in groupes)
    if poids_total == 0:
        return []

    paris: list[tuple[str, list[PartantClasse], float]] = []
    for type_pari, combinaisons in groupes.items():
        part_type = budget * (repartition[type_pari] / poids_total)
        if type_pari == "Quinté Flexi":
            mise_quinte = _calculer_mise_quinte_flexi(len(combinaisons[0]), part_type)
            if mise_quinte is not None:
                paris.append((type_pari, combinaisons[0], mise_quinte))
            continue
        mise_par_pari = round(part_type / len(combinaisons), 2)
        for chevaux in combinaisons:
            paris.append((type_pari, chevaux, mise_par_pari))
    return paris
