"""Prépare les données d'entrée d'une analyse à partir des données collectées —
referme la boucle collecte (src/collecte, src/services/collecte_service.py) ->
analyse (src/services/analyse_service.py), cf. L015 §7.

N'invente aucune donnée : un partant non-partant ou sans cote collectée est exclu
de l'analyse plutôt que de recevoir une valeur fabriquée (cf. L009 §2.1). Même
principe appliqué de façon cohérente aux sous-scores eux-mêmes depuis le
2026-07-10 (cf. PROJECT_STATE.md) : une famille sans donnée exploitable (musique
absente, échantillon jockey/entraîneur/hippodrome trop petit...) est exclue de la
moyenne pondérée du Score TurfIA plutôt que comptée à un score neutre "confiant"
à plein poids — l'ancien comportement plafonnait artificiellement le score de la
quasi-totalité des courses dès qu'une ou plusieurs familles manquaient de
données, ce qui est presque toujours le cas en début de vie du moteur.
"""

from __future__ import annotations

from src.algorithms.indicateurs import (
    calculer_indicateur_forme,
    calculer_indicateur_historique_moteur,
    calculer_indicateur_presse_combine,
    calculer_indicateur_professionnels,
    calculer_indicateur_reussite,
    calculer_indicateur_risque_taille_champ,
    calculer_indicateurs_marche,
)
from src.core.exceptions import ValidationError
from src.core.logging import get_logger
from src.repositories.course_repository import CourseRepository
from src.repositories.statistique_repository import StatistiqueRepository
from src.services.analyse_service import DonneesPartant
from src.services.consensus_presse_service import ConsensusPresseService

logger = get_logger("preparation")


class PreparationDonneesService:
    def __init__(
        self,
        course_repository: CourseRepository,
        statistique_repository: StatistiqueRepository,
        consensus_presse_service: ConsensusPresseService | None = None,
    ) -> None:
        self._courses = course_repository
        self._statistiques = statistique_repository
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

        classements_presse: list[list[int]] = []
        if self._presse is not None:
            classements_presse = self._presse.recuperer_classements_presse(reunion.numero, course.numero)

        conditions_connues = (
            course.distance_id is not None and course.surface_id is not None and course.etat_piste_id is not None
        )

        # Identique pour tous les partants de la course (dépend de l'hippodrome, pas
        # du cheval) : calculé une seule fois hors boucle. `roi` vient d'une colonne
        # DECIMAL (psycopg le retourne en `Decimal`, pas `float`) : conversion
        # explicite avant tout calcul arithmétique pur-Python (cf. `normaliser`).
        stat_hippodrome = self._statistiques.get_dernier_hippodrome(reunion.hippodrome_id)
        roi_hippodrome = (
            float(stat_hippodrome.roi) if stat_hippodrome and stat_hippodrome.roi is not None else None
        )
        score_historique = calculer_indicateur_historique_moteur(
            roi_hippodrome,
            stat_hippodrome.nb_courses if stat_hippodrome else 0,
        )

        donnees_partants: list[DonneesPartant] = []
        for partant, cote, score_marche in zip(partants_exploitables, cotes_ordonnees, scores_marche):
            # `partant.musique` (pas `cheval.musique`) : la musique reflète l'historique
            # du cheval tel que connu au moment de CETTE course précise (cf. PMU,
            # `participant.musique`), pas une valeur partagée/écrasée entre courses —
            # bug réel corrigé le 2026-07-10 : jamais extraite du tout à la collecte
            # (`CollecteService._importer_partant` ignorait ce champ), donc "Forme"
            # valait systématiquement le score neutre pour 100 % des partants
            # (vérifié réellement : 0/609 chevaux avec musique en base).
            sous_scores: dict[str, float] = {"marche": score_marche}

            score_forme = calculer_indicateur_forme(partant.musique)
            if score_forme is not None:
                sous_scores["forme"] = score_forme

            if classements_presse:
                sous_scores["presse"] = calculer_indicateur_presse_combine(classements_presse, partant.numero)

            if partant.jockey_id is not None or partant.entraineur_id is not None:
                score_jockey = (
                    calculer_indicateur_reussite(*self._courses.compter_performances_jockey(partant.jockey_id, course_id))
                    if partant.jockey_id is not None
                    else None
                )
                score_entraineur = (
                    calculer_indicateur_reussite(
                        *self._courses.compter_performances_entraineur(partant.entraineur_id, course_id)
                    )
                    if partant.entraineur_id is not None
                    else None
                )
                score_couple = (
                    calculer_indicateur_reussite(
                        *self._courses.compter_performances_couple(partant.jockey_id, partant.entraineur_id, course_id)
                    )
                    if partant.jockey_id is not None and partant.entraineur_id is not None
                    else None
                )
                score_professionnels = calculer_indicateur_professionnels(score_jockey, score_entraineur, score_couple)
                if score_professionnels is not None:
                    sous_scores["professionnels"] = score_professionnels

            if score_historique is not None:
                sous_scores["historique"] = score_historique

            if conditions_connues:
                score_aptitude = calculer_indicateur_reussite(
                    *self._courses.compter_performances_cheval_conditions(
                        partant.cheval_id, course.distance_id, course.surface_id, course.etat_piste_id, course_id
                    )
                )
                if score_aptitude is not None:
                    sous_scores["aptitude"] = score_aptitude

            donnees_partants.append(
                DonneesPartant(partant_id=partant.id, sous_scores=sous_scores, cote=cote)
            )

        sous_risques_course = {
            # "course" : famille documentée en L031.3 §3 (« Grand nombre de partants »),
            # cf. src/algorithms/risque.py PONDERATIONS_PAR_DEFAUT.
            "course": calculer_indicateur_risque_taille_champ(len(partants_exploitables)),
        }
        return donnees_partants, sous_risques_course
