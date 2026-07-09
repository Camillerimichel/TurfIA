"""Contrôle ROI réel a posteriori (cf. L011 §8.7, L030.4) — ferme la boucle entre
une analyse (pari théorique) et le résultat officiel réel de la course.

Couvre les 6 types de pari construits par `AnalyseService` (cf.
src/algorithms/classement.py, `construire_paris`) : Simple Gagnant/Placé,
Couplé Gagnant/Placé, 2 sur 4, Quinté Flexi. Un type de pari inattendu est
journalisé et ignoré plutôt que deviné, de même qu'un rapport PMU absent pour
le type demandé (ex. Couplé Gagnant sur une course ordinaire qui ne le propose
pas, cf. PROJECT_STATE.md).

Persiste un agrégat par analyse dans `controle_roi` (mise/gains sommés sur tous
les paris) ET un détail par pari dans `controle_roi_pari` — ce dernier est
nécessaire depuis qu'une analyse produit plusieurs types de pari : `pari` seul
ne porte pas le résultat réel, et `controle_roi` (un agrégat par analyse) ne
permet plus de reconstituer le ROI par type sans double-compter (cf.
PROJECT_STATE.md, bug corrigé le 2026-07-08).
"""

from __future__ import annotations

import itertools

from src.algorithms.controle_roi import (
    calculer_gains_couple,
    calculer_gains_deux_sur_quatre,
    calculer_gains_quinte_flexi,
    calculer_gains_simple,
)
from src.collecte.pmu.client import PMUClient
from src.collecte.pmu.mappers import (
    TYPES_PARI_PMU,
    extraire_rapport_couple,
    extraire_rapport_deux_sur_quatre,
    extraire_rapport_quinte,
    extraire_rapport_simple,
)
from src.core.exceptions import ImportationError
from src.core.logging import get_logger
from src.models.analyse import Analyse, ControleRoi, ControleRoiPari, Pari
from src.repositories.analyse_repository import AnalyseRepository
from src.repositories.course_repository import CourseRepository

logger = get_logger("controle_roi")

TYPES_PARI_SIMPLE = ("Simple Gagnant", "Simple Placé")
TYPES_PARI_COUPLE = ("Couplé Gagnant", "Couplé Placé")


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
        except ImportationError as exc:
            logger.warning(
                f"Rapports PMU indisponibles pour l'analyse {analyse.id} (course {analyse.course_id}) : {exc}",
                extra={"context": {"analyse_id": analyse.id, "course_id": analyse.course_id}},
            )
            return None

        cache: dict[str, tuple] = {}
        mise_totale = 0.0
        gains_totaux = 0.0
        for pari in self._analyses.list_paris_by_analyse(analyse.id):
            gains = self.calculer_gains_pari(pari, rapports_bruts, cache, analyse.id)
            if gains is None:
                continue
            mise = float(pari.mise)
            mise_totale += mise
            gains_totaux += gains
            profit_pari = gains - mise
            self._analyses.create_controle_roi_pari(
                ControleRoiPari(
                    pari_id=pari.id,
                    mise=mise,
                    gains=gains,
                    profit=profit_pari,
                    roi=(profit_pari / mise) * 100 if mise else None,
                    valide=gains > mise,
                )
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

    def _resoudre_numeros(self, pari: Pari, analyse_id: int | None) -> list[str] | None:
        if pari.combinaison is None:
            return None
        numeros = []
        for partant_id in pari.combinaison.split("-"):
            partant = self._courses.get_partant(int(partant_id))
            if partant is None:
                logger.warning(
                    f"Partant introuvable pour le pari {pari.id} (combinaison={pari.combinaison}), ignoré.",
                    extra={"context": {"analyse_id": analyse_id}},
                )
                return None
            numeros.append(str(partant.numero))
        return numeros

    def calculer_gains_pari(
        self, pari: Pari, rapports_bruts: list[dict], cache: dict[str, tuple], analyse_id: int | None
    ) -> float | None:
        """Dispatch par type de pari (Simple/Couplé/2 sur 4/Quinté Flexi), déjà
        testé pour le contrôle ROI a posteriori — méthode publique pour être
        réutilisée telle quelle par le moteur de rejeu (`scripts/
        rejouer_versions.py`) sur des `Pari` en mémoire, jamais persistés
        (`id=None`, utilisé seulement dans les messages de log ci-dessous)."""
        type_pari = pari.type_pari
        if type_pari not in TYPES_PARI_PMU:
            logger.warning(
                f"Pari {pari.id} (type='{type_pari}') non pris en charge par le contrôle ROI, ignoré.",
                extra={"context": {"analyse_id": analyse_id}},
            )
            return None

        numeros = self._resoudre_numeros(pari, analyse_id)
        if numeros is None:
            return None
        mise = float(pari.mise)

        try:
            if type_pari in TYPES_PARI_SIMPLE:
                if type_pari not in cache:
                    cache[type_pari] = extraire_rapport_simple(rapports_bruts, TYPES_PARI_PMU[type_pari])
                dividendes, rembourse = cache[type_pari]
                return calculer_gains_simple(mise, numeros[0], dividendes, rembourse)

            if type_pari in TYPES_PARI_COUPLE:
                if type_pari not in cache:
                    cache[type_pari] = extraire_rapport_couple(rapports_bruts, TYPES_PARI_PMU[type_pari])
                dividendes, rembourse = cache[type_pari]
                return calculer_gains_couple(mise, frozenset(numeros), dividendes, rembourse)

            if type_pari == "2 sur 4":
                if type_pari not in cache:
                    cache[type_pari] = extraire_rapport_deux_sur_quatre(rapports_bruts)
                numeros_arrivee, dividende, rembourse = cache[type_pari]
                return calculer_gains_deux_sur_quatre(mise, frozenset(numeros), numeros_arrivee, dividende, rembourse)

            if type_pari == "Quinté Flexi":
                if type_pari not in cache:
                    cache[type_pari] = extraire_rapport_quinte(rapports_bruts)
                rapport = cache[type_pari]
                sous_combinaisons = [frozenset(c) for c in itertools.combinations(numeros, 5)]
                if not sous_combinaisons:
                    return None
                mise_par_combinaison = mise / len(sous_combinaisons)
                return calculer_gains_quinte_flexi(
                    mise_par_combinaison, sous_combinaisons, rapport.numeros_arrivee, rapport.dividende_desordre,
                    rapport.dividendes_bonus4, rapport.dividendes_bonus3, rapport.rembourse,
                )
        except ImportationError as exc:
            logger.warning(
                f"Rapport PMU '{type_pari}' indisponible pour le pari {pari.id} (analyse {analyse_id}) : {exc}",
                extra={"context": {"analyse_id": analyse_id}},
            )
            return None

        return None
