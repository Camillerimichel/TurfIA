"""Prépare les données d'entrée d'une analyse à partir des données collectées —
referme la boucle collecte (src/collecte, src/services/collecte_service.py) ->
analyse (src/services/analyse_service.py), cf. L015 §7.

N'invente aucune donnée : un partant non-partant ou sans cote collectée est exclu
de l'analyse plutôt que de recevoir une valeur fabriquée (cf. L009 §2.1).
"""

from __future__ import annotations

from src.algorithms.indicateurs import (
    calculer_indicateur_forme,
    calculer_indicateur_risque_taille_champ,
    calculer_indicateurs_marche,
)
from src.core.exceptions import ValidationError
from src.core.logging import get_logger
from src.repositories.course_repository import CourseRepository
from src.services.analyse_service import DonneesPartant

logger = get_logger("preparation")


class PreparationDonneesService:
    def __init__(self, course_repository: CourseRepository) -> None:
        self._courses = course_repository

    def preparer_donnees_partants(self, course_id: int) -> tuple[list[DonneesPartant], dict[str, float]]:
        """Retourne les données de partants prêtes pour `AnalyseService.analyser_course`,
        ainsi que les sous-risques de la course.
        """
        tous_partants = self._courses.list_partants_by_course(course_id)
        cotes_par_partant = self._courses.get_dernieres_cotes_par_course(course_id)

        partants_exploitables = [p for p in tous_partants if not p.non_partant and p.id in cotes_par_partant]
        nb_exclus = len(tous_partants) - len(partants_exploitables)
        if nb_exclus:
            logger.warning(
                f"{nb_exclus} partant(s) exclu(s) de l'analyse (non-partant ou cote non collectée).",
                extra={"context": {"course_id": course_id}},
            )
        if not partants_exploitables:
            raise ValidationError(f"Aucun partant exploitable pour la course {course_id}.")

        cotes_ordonnees = [cotes_par_partant[p.id] for p in partants_exploitables]
        scores_marche = calculer_indicateurs_marche(cotes_ordonnees)

        donnees_partants: list[DonneesPartant] = []
        for partant, cote, score_marche in zip(partants_exploitables, cotes_ordonnees, scores_marche):
            cheval = self._courses.get_cheval(partant.cheval_id)
            score_forme = calculer_indicateur_forme(cheval.musique if cheval else None)
            donnees_partants.append(
                DonneesPartant(
                    partant_id=partant.id,
                    sous_scores={"marche": score_marche, "forme": score_forme},
                    cote=cote,
                )
            )

        sous_risques_course = {
            # "course" : famille documentée en L031.3 §3 (« Grand nombre de partants »),
            # cf. src/algorithms/risque.py PONDERATIONS_PAR_DEFAUT.
            "course": calculer_indicateur_risque_taille_champ(len(partants_exploitables)),
        }
        return donnees_partants, sous_risques_course
