"""Prépare les données d'entrée d'une analyse à partir des données collectées —
referme la boucle collecte (src/collecte, src/services/collecte_service.py) ->
analyse (src/services/analyse_service.py), cf. L015 §7.

N'invente aucune donnée : un partant non-partant ou sans cote collectée est exclu
de l'analyse plutôt que de recevoir une valeur fabriquée (cf. L009 §2.1).
"""

from __future__ import annotations

from src.algorithms.indicateurs import (
    SCORE_NEUTRE_PAR_DEFAUT,
    calculer_indicateur_forme,
    calculer_indicateur_presse,
    calculer_indicateur_professionnels,
    calculer_indicateur_reussite,
    calculer_indicateur_risque_taille_champ,
    calculer_indicateurs_marche,
)
from src.core.exceptions import ImportationError, ValidationError
from src.core.logging import get_logger
from src.repositories.course_repository import CourseRepository
from src.services.analyse_service import DonneesPartant
from src.services.consensus_presse_service import ConsensusPresseService

logger = get_logger("preparation")


class PreparationDonneesService:
    def __init__(
        self,
        course_repository: CourseRepository,
        consensus_presse_service: ConsensusPresseService | None = None,
    ) -> None:
        self._courses = course_repository
        self._presse = consensus_presse_service

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

        course = self._courses.get_course(course_id)
        reunion = self._courses.get_reunion(course.reunion_id)

        classement_presse: list[int] | None = None
        if self._presse is not None:
            try:
                classement_presse = self._presse.recuperer_classement_presse(reunion.numero, course.numero)
            except ImportationError as exc:
                logger.warning(
                    f"Consensus presse indisponible, analyse poursuivie sans ce sous-score : {exc}",
                    extra={"context": {"course_id": course_id}},
                )

        conditions_connues = (
            course.distance_id is not None and course.surface_id is not None and course.etat_piste_id is not None
        )

        donnees_partants: list[DonneesPartant] = []
        for partant, cote, score_marche in zip(partants_exploitables, cotes_ordonnees, scores_marche):
            cheval = self._courses.get_cheval(partant.cheval_id)
            score_forme = calculer_indicateur_forme(cheval.musique if cheval else None)
            sous_scores = {"marche": score_marche, "forme": score_forme}
            if classement_presse is not None:
                sous_scores["presse"] = calculer_indicateur_presse(classement_presse, partant.numero)

            if partant.jockey_id is not None or partant.entraineur_id is not None:
                score_jockey = (
                    calculer_indicateur_reussite(*self._courses.compter_performances_jockey(partant.jockey_id, course_id))
                    if partant.jockey_id is not None
                    else SCORE_NEUTRE_PAR_DEFAUT
                )
                score_entraineur = (
                    calculer_indicateur_reussite(
                        *self._courses.compter_performances_entraineur(partant.entraineur_id, course_id)
                    )
                    if partant.entraineur_id is not None
                    else SCORE_NEUTRE_PAR_DEFAUT
                )
                score_couple = (
                    calculer_indicateur_reussite(
                        *self._courses.compter_performances_couple(partant.jockey_id, partant.entraineur_id, course_id)
                    )
                    if partant.jockey_id is not None and partant.entraineur_id is not None
                    else SCORE_NEUTRE_PAR_DEFAUT
                )
                sous_scores["professionnels"] = calculer_indicateur_professionnels(
                    score_jockey, score_entraineur, score_couple
                )

            sous_scores["historique"] = calculer_indicateur_reussite(
                *self._courses.compter_performances_cheval_hippodrome(partant.cheval_id, reunion.hippodrome_id, course_id)
            )

            if conditions_connues:
                sous_scores["aptitude"] = calculer_indicateur_reussite(
                    *self._courses.compter_performances_cheval_conditions(
                        partant.cheval_id, course.distance_id, course.surface_id, course.etat_piste_id, course_id
                    )
                )

            donnees_partants.append(
                DonneesPartant(partant_id=partant.id, sous_scores=sous_scores, cote=cote)
            )

        sous_risques_course = {
            # "course" : famille documentée en L031.3 §3 (« Grand nombre de partants »),
            # cf. src/algorithms/risque.py PONDERATIONS_PAR_DEFAUT.
            "course": calculer_indicateur_risque_taille_champ(len(partants_exploitables)),
        }
        return donnees_partants, sous_risques_course
