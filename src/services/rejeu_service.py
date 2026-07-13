"""Service du moteur de rejeu/backtesting (cf. L031.7 §4) — extrait de
`scripts/rejouer_versions.py` pour être réutilisable depuis l'API (cf.
`POST /administration/rejeu`) sans dupliquer la logique, même principe que les
3 autres automatisations déjà exposées à la fois en script CLI et en route
(L033 ADR-002). Le script CLI reste le point d'entrée en ligne de commande,
appelle désormais cette même classe.

Compare le ROI d'un jeu de poids_score/poids_risque sur un historique de
courses réelles déjà arrivées, à budget constant. Ne modifie jamais
`analyses`/`pari`/`controle_roi` (persistance légère : une seule ligne de
synthèse dans `statistique_modele` par exécution, `source="rejeu"`).

Hors périmètre (limites déjà existantes, héritées telles quelles) : le
consensus Presse n'est pas rejouable (`ConsensusPresseService` scrape en
direct, uniquement le Quinté+ du jour même) — non branché ici. La famille
Historique reflète l'état *actuel* de `statistique_hippodrome`, pas un
instantané au moment de la course rejouée. Les familles Value/Contexte ne
sont jamais produites. Les seuils de décision (`determiner_decision`) ne
sont pas paramétrables, seuls les poids le sont.
"""

from __future__ import annotations

import json
from datetime import date

from src.algorithms.rejeu import (
    agreger_par_hippodrome,
    agreger_par_tranche_score,
    agreger_par_type_pari,
    agreger_resultats_rejeu,
    calculer_drawdown,
    calculer_stabilite,
    serialiser_liste_stats,
)
from src.collecte.pmu.client import PMUClient
from src.core.exceptions import ImportationError, ValidationError
from src.core.logging import get_logger
from src.models.statistique import StatistiqueModele
from src.repositories.analyse_repository import AnalyseRepository
from src.repositories.course_repository import CourseRepository
from src.repositories.statistique_repository import StatistiqueRepository
from src.services.analyse_service import AnalyseService
from src.services.controle_roi_service import ControleRoiService
from src.services.preparation_service import PreparationDonneesService

logger = get_logger("rejeu")


class RejeuService:
    def __init__(
        self,
        pmu_client: PMUClient,
        course_repository: CourseRepository,
        analyse_repository: AnalyseRepository,
        statistique_repository: StatistiqueRepository,
    ) -> None:
        self._pmu = pmu_client
        self._courses = course_repository
        self._analyses = analyse_repository
        self._statistiques = statistique_repository

    def rejouer(
        self,
        version_modele: str,
        date_debut: date,
        date_fin: date,
        poids_score: dict[str, float] | None = None,
        poids_risque: dict[str, float] | None = None,
        commentaire: str | None = None,
    ) -> StatistiqueModele:
        preparation = PreparationDonneesService(self._courses, self._statistiques)
        analyse_service = AnalyseService(self._analyses, poids_score=poids_score, poids_risque=poids_risque)
        controle_roi_service = ControleRoiService(self._pmu, self._analyses, self._courses)

        courses = self._courses.list_courses_avec_resultat(date_debut, date_fin)

        resultats_paris: list[tuple[float, float, bool]] = []
        resultats_courses_score: list[tuple[float, float, float]] = []
        resultats_courses_hippodrome: list[tuple[int, float, float]] = []
        resultats_paris_type: list[tuple[str, float, float]] = []
        profits_chronologiques: list[float] = []
        rois_par_course: list[float] = []
        nb_courses_rejouees = 0
        for course in courses:
            try:
                donnees_partants, sous_risques_course = preparation.preparer_donnees_partants(course.id)
            except ValidationError as exc:
                logger.warning(f"Course {course.id} ignorée (préparation) : {exc}")
                continue

            resultat = analyse_service.analyser_course(
                course_id=course.id,
                version=1,
                partants=donnees_partants,
                sous_risques_course=sous_risques_course,
                persister=False,
                quinte=course.quinte,
            )
            if not resultat.paris:
                continue

            reunion = self._courses.get_reunion(course.reunion_id)
            try:
                rapports_bruts = self._pmu.recuperer_rapports_definitifs(reunion.date, reunion.numero, course.numero)
            except ImportationError as exc:
                logger.warning(f"Rapports PMU indisponibles pour la course {course.id} : {exc}")
                continue

            cache: dict[str, tuple] = {}
            mise_course = 0.0
            gains_course = 0.0
            for pari in resultat.paris:
                gains = controle_roi_service.calculer_gains_pari(pari, rapports_bruts, cache, analyse_id=None)
                if gains is None:
                    continue
                mise = float(pari.mise)
                resultats_paris.append((mise, gains, gains > mise))
                resultats_paris_type.append((pari.type_pari, mise, gains))
                mise_course += mise
                gains_course += gains

            if mise_course == 0:
                continue

            nb_courses_rejouees += 1
            resultats_courses_score.append((resultat.analyse.score_confiance, mise_course, gains_course))
            resultats_courses_hippodrome.append((reunion.hippodrome_id, mise_course, gains_course))
            profits_chronologiques.append(gains_course - mise_course)
            rois_par_course.append(((gains_course - mise_course) / mise_course) * 100)

        nb_paris, roi, taux_reussite = agreger_resultats_rejeu(resultats_paris)
        parametres = json.dumps({"poids_score": poids_score, "poids_risque": poids_risque})
        return self._statistiques.create_modele(
            StatistiqueModele(
                version_modele=version_modele,
                date_debut=date_debut,
                date_fin=date_fin,
                nb_courses=nb_courses_rejouees,
                roi=roi,
                taux_reussite=taux_reussite,
                roi_par_score=serialiser_liste_stats(agreger_par_tranche_score(resultats_courses_score)),
                roi_par_hippodrome=serialiser_liste_stats(agreger_par_hippodrome(resultats_courses_hippodrome)),
                roi_par_type_pari=serialiser_liste_stats(agreger_par_type_pari(resultats_paris_type)),
                drawdown=calculer_drawdown(profits_chronologiques),
                stabilite=calculer_stabilite(rois_par_course),
                parametres=parametres,
                commentaire=commentaire,
                source="rejeu",
            )
        )
