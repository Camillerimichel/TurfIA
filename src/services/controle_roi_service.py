"""Contrôle ROI réel a posteriori (cf. L011 §8.7, L030.4) — ferme la boucle entre
une analyse (pari théorique) et le résultat officiel réel de la course.

Périmètre volontaire : seuls les paris de type « Simple Gagnant » sont contrôlés
(le seul type généré par `AnalyseService` aujourd'hui, cf.
src/services/analyse_service.py) contre le rapport PMU réel (cf.
src/collecte/pmu/mappers.py, `extraire_rapport_simple_gagnant`). Un autre type de
pari rencontré est journalisé et ignoré plutôt que deviné.
"""

from __future__ import annotations

from src.algorithms.controle_roi import calculer_gains_simple_gagnant
from src.collecte.pmu.client import PMUClient
from src.collecte.pmu.mappers import extraire_rapport_simple_gagnant
from src.core.exceptions import ImportationError
from src.core.logging import get_logger
from src.models.analyse import Analyse, ControleRoi
from src.repositories.analyse_repository import AnalyseRepository
from src.repositories.course_repository import CourseRepository

logger = get_logger("controle_roi")

TYPE_PARI_CONTROLE = "Simple Gagnant"


class ControleRoiService:
    def __init__(
        self, pmu_client: PMUClient, analyse_repository: AnalyseRepository, course_repository: CourseRepository
    ) -> None:
        self._pmu = pmu_client
        self._analyses = analyse_repository
        self._courses = course_repository

    def calculer_controles_manquants(self) -> list[ControleRoi]:
        """Calcule et persiste le contrôle ROI de chaque analyse qui en manque
        encore. L'échec d'une analyse (rapport PMU pas encore disponible, réseau)
        est journalisé et n'empêche jamais les suivantes (cf. isolation déjà en
        place dans `CollecteService`/`ConsensusPresseService`)."""
        controles: list[ControleRoi] = []
        for analyse in self._analyses.list_analyses_sans_controle_roi():
            controle = self._calculer_un_controle(analyse)
            if controle is not None:
                controles.append(controle)
        return controles

    def _calculer_un_controle(self, analyse: Analyse) -> ControleRoi | None:
        course = self._courses.get_course(analyse.course_id)
        reunion = self._courses.get_reunion(course.reunion_id)

        try:
            rapports_bruts = self._pmu.recuperer_rapports_definitifs(reunion.date, reunion.numero, course.numero)
            combinaison_gagnante, dividende, rembourse = extraire_rapport_simple_gagnant(rapports_bruts)
        except ImportationError as exc:
            logger.warning(
                f"Rapports PMU indisponibles pour l'analyse {analyse.id} (course {analyse.course_id}) : {exc}",
                extra={"context": {"analyse_id": analyse.id, "course_id": analyse.course_id}},
            )
            return None

        mise_totale = 0.0
        gains_totaux = 0.0
        for pari in self._analyses.list_paris_by_analyse(analyse.id):
            if pari.type_pari != TYPE_PARI_CONTROLE or pari.combinaison is None:
                logger.warning(
                    f"Pari {pari.id} (type='{pari.type_pari}') non pris en charge par le contrôle ROI, ignoré.",
                    extra={"context": {"analyse_id": analyse.id}},
                )
                continue
            partant = self._courses.get_partant(int(pari.combinaison))
            if partant is None:
                logger.warning(
                    f"Partant introuvable pour le pari {pari.id} (combinaison={pari.combinaison}), ignoré.",
                    extra={"context": {"analyse_id": analyse.id}},
                )
                continue
            mise_totale += pari.mise
            gains_totaux += calculer_gains_simple_gagnant(
                pari.mise, str(partant.numero), combinaison_gagnante, dividende, rembourse
            )

        if mise_totale == 0:
            return None

        profit = gains_totaux - mise_totale
        return self._analyses.create_controle_roi(
            ControleRoi(
                analyse_id=analyse.id,
                mise=mise_totale,
                gains=gains_totaux,
                profit=profit,
                roi=(profit / mise_totale) * 100,
                valide=gains_totaux > mise_totale,
            )
        )
