"""Agrégation pure du moteur de rejeu/backtesting (cf. L031.7 §4-5) — fonctions
pures (cf. L006 §4.2), aucun accès réseau ou base ici.

Ne fait qu'agréger des résultats de paris déjà contrôlés contre des rapports
PMU réels (cf. `ControleRoiService.calculer_gains_pari`, réutilisé tel quel par
`scripts/rejouer_versions.py`) — le rejeu ne réimplémente aucune logique de
calcul de gains, seulement la synthèse des indicateurs L031.7 §5 sur
l'ensemble rejoué (ROI global, ROI par tranche de score/hippodrome/type de
pari, drawdown, stabilité), à la manière de `StatistiqueRepository` (mêmes
formules, mêmes tranches).
"""

from __future__ import annotations

import dataclasses
import json
import statistics

from src.algorithms.score import SEUILS_DECISION_PAR_DEFAUT
from src.models.statistique import StatistiqueHippodrome, StatistiquePari, StatistiqueScore


def agreger_resultats_rejeu(
    resultats_paris: list[tuple[float, float, bool]],
) -> tuple[int, float | None, float | None]:
    """`resultats_paris` : une entrée `(mise, gains, valide)` par pari contrôlé
    sur l'ensemble de l'historique rejoué. Retourne `(nb_paris, roi,
    taux_reussite)` — `roi`/`taux_reussite` sont `None` si `resultats_paris` est
    vide (rien à diviser).
    """
    nb_paris = len(resultats_paris)
    if nb_paris == 0:
        return 0, None, None

    mise_totale = sum(mise for mise, _, _ in resultats_paris)
    gains_totaux = sum(gains for _, gains, _ in resultats_paris)
    nb_valides = sum(1 for _, _, valide in resultats_paris if valide)

    roi = ((gains_totaux - mise_totale) / mise_totale) * 100 if mise_totale else None
    taux_reussite = (nb_valides / nb_paris) * 100

    return nb_paris, roi, taux_reussite


def agreger_par_tranche_score(
    resultats_courses: list[tuple[float, float, float]],
) -> list[StatistiqueScore]:
    """`resultats_courses` : un triplet `(score_confiance, mise_totale_course,
    gains_totaux_course)` par course rejouée (mise/gains sommés sur tous les
    paris de la course, comme `controle_roi` le fait déjà pour l'agrégat par
    analyse — le score de confiance est un attribut de la course, pas du pari).
    Regroupe selon les mêmes tranches que `StatistiqueRepository.
    calculer_scores` (`SEUILS_DECISION_PAR_DEFAUT`, une seule source de
    vérité, même borne haute incluse sur la dernière tranche). Une tranche sans
    course rejouée est omise du résultat — de même qu'une course dont le score
    dépasserait 100 (`calculer_score_final` n'écrête pas le bonus value bet,
    limite déjà présente dans `calculer_scores`, héritée telle quelle ici).
    """
    seuil_prudent, seuil_normal, seuil_opportunite = SEUILS_DECISION_PAR_DEFAUT
    tranches = [(0.0, seuil_prudent), (seuil_prudent, seuil_normal), (seuil_normal, seuil_opportunite), (seuil_opportunite, 100.0)]

    resultats: list[StatistiqueScore] = []
    for index, (score_min, score_max) in enumerate(tranches):
        dernier = index == len(tranches) - 1
        courses = [
            (mise, gains)
            for score, mise, gains in resultats_courses
            if (score_min <= score < score_max) or (dernier and score_min <= score <= score_max)
        ]
        nb_courses = len(courses)
        if nb_courses == 0:
            continue
        nb_gagnantes = sum(1 for mise, gains in courses if gains > mise)
        mise_totale = sum(mise for mise, _ in courses)
        gains_totaux = sum(gains for _, gains in courses)
        resultats.append(
            StatistiqueScore(
                score_min=score_min,
                score_max=score_max,
                nb_courses=nb_courses,
                nb_gagnantes=nb_gagnantes,
                roi=((gains_totaux - mise_totale) / mise_totale) * 100 if mise_totale else None,
                taux_reussite=(nb_gagnantes / nb_courses) * 100,
            )
        )
    return resultats


def agreger_par_hippodrome(resultats_courses: list[tuple[int, float, float]]) -> list[StatistiqueHippodrome]:
    """`resultats_courses` : un triplet `(hippodrome_id, mise_totale_course,
    gains_totaux_course)` par course rejouée."""
    par_hippodrome: dict[int, list[tuple[float, float]]] = {}
    for hippodrome_id, mise, gains in resultats_courses:
        par_hippodrome.setdefault(hippodrome_id, []).append((mise, gains))

    resultats: list[StatistiqueHippodrome] = []
    for hippodrome_id, courses in par_hippodrome.items():
        mise_totale = sum(mise for mise, _ in courses)
        gains_totaux = sum(gains for _, gains in courses)
        profit = gains_totaux - mise_totale
        resultats.append(
            StatistiqueHippodrome(
                hippodrome_id=hippodrome_id,
                nb_courses=len(courses),
                mises=mise_totale,
                gains=gains_totaux,
                profit=profit,
                roi=(profit / mise_totale) * 100 if mise_totale else None,
            )
        )
    return resultats


def agreger_par_type_pari(resultats_paris: list[tuple[str, float, float]]) -> list[StatistiquePari]:
    """`resultats_paris` : un triplet `(type_pari, mise, gains)` par pari
    contrôlé — granularité par pari (pas par course), plusieurs types
    coexistant au sein d'une même course."""
    par_type: dict[str, list[tuple[float, float]]] = {}
    for type_pari, mise, gains in resultats_paris:
        par_type.setdefault(type_pari, []).append((mise, gains))

    resultats: list[StatistiquePari] = []
    for type_pari, paris in par_type.items():
        mise_totale = sum(mise for mise, _ in paris)
        gains_totaux = sum(gains for _, gains in paris)
        profit = gains_totaux - mise_totale
        nb_gagnants = sum(1 for mise, gains in paris if gains > mise)
        resultats.append(
            StatistiquePari(
                type_pari=type_pari,
                nb_paris=len(paris),
                mises=mise_totale,
                gains=gains_totaux,
                profit=profit,
                roi=(profit / mise_totale) * 100 if mise_totale else None,
                taux_reussite=(nb_gagnants / len(paris)) * 100,
            )
        )
    return resultats


def calculer_drawdown(profits_chronologiques: list[float]) -> float | None:
    """Perte maximale (en euros) entre un sommet et un creux ultérieur sur la
    courbe de profit cumulé, dans l'ordre chronologique des courses rejouées.
    `None` si aucune course. Choix assumé (L031.7 §5 ne précise pas de
    formule) : exprimé en euros absolus plutôt qu'en pourcentage — un pic
    cumulé nul ou négatif en tout début de séquence rendrait un pourcentage
    non défini.
    """
    if not profits_chronologiques:
        return None
    cumul = 0.0
    pic = 0.0
    pire_baisse = 0.0
    for profit in profits_chronologiques:
        cumul += profit
        pic = max(pic, cumul)
        pire_baisse = max(pire_baisse, pic - cumul)
    return round(pire_baisse, 2)


def calculer_stabilite(rois_par_course: list[float]) -> float | None:
    """Écart-type (population) du ROI par course sur l'ensemble rejoué — plus
    bas = plus stable. `None` si aucune course. Choix assumé (L031.7 §5 ne
    précise pas de formule).
    """
    if not rois_par_course:
        return None
    return round(statistics.pstdev(rois_par_course), 2)


def serialiser_liste_stats(objets: list) -> str:
    """Sérialise une liste de dataclasses (`StatistiqueScore`/
    `StatistiqueHippodrome`/`StatistiquePari`) en JSON — même esprit que
    `src/core/audit.py::serialiser_etat`, mais pour une liste plutôt qu'un
    objet unique (les deux cas d'usage sont distincts, pas de réutilisation
    directe possible)."""
    return json.dumps([dataclasses.asdict(o) for o in objets], default=str, ensure_ascii=False)
