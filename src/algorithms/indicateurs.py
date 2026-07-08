"""Calcul d'indicateurs réels à partir des données collectées — cf. L031.2 §3
(familles Marché, Forme, Presse, Professionnels, Historique et Aptitude), fonctions
pures (cf. L006 §4.2).

« Historique » et « Aptitude » sont interprétées selon L031.1 §5 (performance passée
du cheval à l'hippodrome, respectivement dans les mêmes distance/surface/état de
piste) — la définition littérale de L031.2 (« performances TurfIA passées ») relève
du futur module Statistiques (L031.7), non construit ici (cf. PROJECT_STATE.md).
"""

from __future__ import annotations

import re

from src.algorithms.normalisation import normaliser
from src.algorithms.roi_theorique import probabilites_implicites_normalisees
from src.core.constants import SCORE_MAX

SCORE_NEUTRE_PAR_DEFAUT = 50.0
POSITION_NON_NUMERIQUE_OU_ZERO = 10  # cf. §parser_musique : incident ou 10e et au-delà

_MARQUEUR_ANNEE = re.compile(r"\(\d+\)")


def parser_musique(musique: str | None) -> list[int]:
    """Extrait les positions passées d'une chaîne « musique » PMU, la plus récente
    en premier (cf. échantillons réels capturés le 2026-07-07, ex. `"5p7p0p0p"`).

    Chaque résultat passé est codé sur deux caractères : une position (1-9) ou un
    code d'incident (lettre : arrêté, tombé, distancé...), suivi d'une lettre de
    discipline. Les marqueurs d'année entre parenthèses (ex. `"(25)"`) sont retirés.

    Faute de pouvoir distinguer de façon fiable la nature exacte de chaque incident
    non numérique depuis ce seul champ, tout code non numérique est traité comme
    équivalent à « 10e et au-delà » (même turpitude qu'un `0`) plutôt que deviné.
    """
    if not musique:
        return []

    sans_annees = _MARQUEUR_ANNEE.sub("", musique)
    positions: list[int] = []
    i = 0
    while i < len(sans_annees):
        code = sans_annees[i]
        i += 1
        while i < len(sans_annees) and sans_annees[i].isalpha():
            i += 1
        if code.isdigit():
            valeur = int(code)
            positions.append(valeur if valeur != 0 else POSITION_NON_NUMERIQUE_OU_ZERO)
        else:
            positions.append(POSITION_NON_NUMERIQUE_OU_ZERO)
    return positions


def calculer_indicateur_forme(musique: str | None, nb_courses: int = 5) -> float:
    """Sous-score « Forme » (cf. L031.2 §5, famille Forme) : moyenne normalisée des
    `nb_courses` dernières positions (1re place -> proche de 100, 10e et au-delà ou
    incident -> proche de 0). Retourne un score neutre si aucune donnée disponible.
    """
    positions = parser_musique(musique)[:nb_courses]
    if not positions:
        return SCORE_NEUTRE_PAR_DEFAUT
    scores = [normaliser(p, minimum=1, maximum=POSITION_NON_NUMERIQUE_OU_ZERO, inverse=True) for p in positions]
    return sum(scores) / len(scores)


def calculer_indicateurs_marche(cotes: list[float | None]) -> list[float]:
    """Sous-score « Marché » par partant (cf. L031.2 §5, famille Marché) : probabilité
    implicite du marché (marge neutralisée, cf. `probabilites_implicites_normalisees`)
    normalisée sur [0, 100] relativement au champ. Un partant sans cote connue reçoit
    un score neutre plutôt que de fausser le calcul du champ.

    Retourne une liste dans le même ordre que `cotes`.
    """
    cotes_connues = [c for c in cotes if c is not None]
    if not cotes_connues:
        return [SCORE_NEUTRE_PAR_DEFAUT] * len(cotes)

    probabilites = probabilites_implicites_normalisees(cotes_connues)
    minimum, maximum = min(probabilites), max(probabilites)

    resultats: list[float] = []
    it = iter(probabilites)
    for cote in cotes:
        if cote is None:
            resultats.append(SCORE_NEUTRE_PAR_DEFAUT)
        else:
            resultats.append(normaliser(next(it), minimum, maximum) if maximum != minimum else SCORE_MAX / 2)
    return resultats


def calculer_indicateur_presse(classement_numeros: list[int], numero_partant: int) -> float:
    """Sous-score « Presse » (cf. L031.2 §Presse, consensus multi-journaux) : rang du
    partant dans un classement consensus (Canalturf ou Zone-Turf, cf.
    `calculer_indicateur_presse_combine`), 1er cité -> proche de 100, normalisé sur
    le nombre de chevaux cités. Un partant non cité par la presse reçoit le rang
    « pire que le dernier cité » (`len(classement_numeros) + 1`) : approximation
    faute de disposer d'un nombre de citations par cheval.

    Précondition : `classement_numeros` non vide (l'appelant ne doit invoquer cette
    fonction que lorsqu'un classement a effectivement été obtenu).
    """
    pire_rang = len(classement_numeros) + 1
    try:
        rang = classement_numeros.index(numero_partant) + 1
    except ValueError:
        rang = pire_rang
    return normaliser(rang, minimum=1, maximum=pire_rang, inverse=True)


def calculer_indicateur_presse_combine(classements: list[list[int]], numero_partant: int) -> float:
    """Combine les sous-scores Presse de plusieurs sources de consensus
    (aujourd'hui Canalturf et Zone-Turf, cf. `src/services/consensus_presse_service.py`) :
    moyenne simple des scores individuels, même logique que
    `calculer_indicateur_professionnels` — aucune source ne domine les autres,
    aucune pondération distincte entre elles n'est documentée.

    Précondition : `classements` non vide (l'appelant ne l'invoque que si au moins
    une source a répondu).
    """
    scores = [calculer_indicateur_presse(classement, numero_partant) for classement in classements]
    return sum(scores) / len(scores)


def calculer_indicateur_reussite(nb_victoires: int, nb_courses: int, minimum_courses: int = 3) -> float:
    """Sous-score de réussite (victoires / courses disputées), utilisé pour les
    familles Historique (performance du cheval à l'hippodrome, cf. L031.1 §5) et
    Aptitude (mêmes distance/surface/état de piste, cf. L031.2 §Aptitude), ainsi que
    pour chacune des 3 variables de Professionnels (cf. `calculer_indicateur_professionnels`).

    Retourne un score neutre si l'échantillon est trop petit (`nb_courses <
    minimum_courses`) pour être statistiquement significatif, plutôt que de faire
    reposer le score sur 1 ou 2 courses.
    """
    if nb_courses < minimum_courses:
        return SCORE_NEUTRE_PAR_DEFAUT
    return normaliser(nb_victoires / nb_courses, minimum=0.0, maximum=1.0)


def calculer_indicateur_professionnels(score_jockey: float, score_entraineur: float, score_couple: float) -> float:
    """Sous-score « Professionnels » (cf. L031.2 §Professionnels) : moyenne simple des
    3 variables documentées (réussite jockey, réussite entraîneur, réussite du
    couple) — aucune pondération distincte entre elles n'est documentée."""
    return (score_jockey + score_entraineur + score_couple) / 3


def calculer_indicateur_risque_taille_champ(nb_partants: int, minimum: int = 4, maximum: int = 20) -> float:
    """Approximation partielle du risque de la course (cf. L031.3 §3, famille
    Course) : un champ nombreux est associé à une incertitude plus élevée. Les
    autres facteurs documentés (volatilité du marché, désaccord presse, changement
    de terrain) ne sont pas calculés dans cette tranche (cf. PROJECT_STATE.md).
    """
    return normaliser(nb_partants, minimum, maximum)
