"""Orchestration des automatisations déclenchées manuellement depuis le module
Administration (cf. L018 §10, L033 ADR-002 : jamais de logique dupliquée,
uniquement les services déjà utilisés par l'API/les scripts CLI).

`collecter_jour`/`calculer_statistiques` délèguent directement à
`CollecteService`/`ControleRoiService`/`StatistiqueService` (mêmes services que
`scripts/collecter_programme.py`/`scripts/calculer_statistiques.py`) ; seule
`analyser_courses_du_jour` est une orchestration nouvelle (aucun script
existant ne traite plus d'une course à la fois, cf. `scripts/analyser_course.py`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from src.repositories.course_repository import CourseRepository
from src.services.analyse_service import AnalyseService
from src.services.preparation_service import PreparationDonneesService


@dataclass(frozen=True)
class RapportAnalyseJour:
    nb_courses: int
    nb_erreurs: int
    nb_deja_parties: int = 0
    erreurs: list[tuple[int, str]] = field(default_factory=list)


class AutomatisationService:
    def __init__(
        self,
        course_repository: CourseRepository,
        preparation: PreparationDonneesService,
        analyse_service: AnalyseService,
    ) -> None:
        self._courses = course_repository
        self._preparation = preparation
        self._analyse_service = analyse_service

    def analyser_courses_du_jour(self, jour: date, maintenant: datetime | None = None) -> RapportAnalyseJour:
        """Relance `preparer_donnees_partants` + `analyser_course` pour chaque
        course des réunions de `jour` pas encore partie (même enchaînement que
        `POST /courses/{id}/analyses/auto`, une course à la fois). Une course en
        erreur n'interrompt pas les autres : toute exception est capturée ici,
        pas seulement `ValidationError`/`BusinessRuleError` (cf. bug réel du
        2026-07-11 — une `CheckViolation` SQL imprévue faisait planter tout le
        lot, effaçant même la trace de la tentative dans `tache`, cf.
        PROJECT_STATE.md), même motif d'isolation par élément que
        `CollecteService.collecter_programme_du_jour`.

        Ce service est relancé toutes les heures (cf. L033,
        `scripts/rafraichir_et_analyser_jour.py`) pour capter les courses dont
        les cotes viennent d'être publiées et, plus généralement, refléter les
        dernières données collectées : chaque passage vise systématiquement la
        version suivante (`AnalyseService.prochaine_version`), jamais la même
        que la fois précédente — la décision jouer/ne pas jouer peut donc
        changer d'une heure à l'autre dans les deux sens (vérifié réellement :
        avant ce fonctionnement, retenter la même version faisait remonter
        `echec` à chaque exécution horaire après la première du jour).

        Une course dont le départ est déjà passé est ignorée (`nb_deja_parties`) :
        au-delà de l'heure de départ, les paris sont clos et une nouvelle
        analyse n'a plus d'utilité opérationnelle."""
        maintenant = maintenant if maintenant is not None else datetime.now()
        nb_courses = 0
        nb_deja_parties = 0
        erreurs: list[tuple[int, str]] = []
        for reunion in self._courses.list_reunions_by_date(jour):
            for course in self._courses.list_courses_by_reunion(reunion.id):
                if course.heure_depart is not None and course.heure_depart <= maintenant:
                    nb_deja_parties += 1
                    continue
                try:
                    donnees_partants, sous_risques_course = self._preparation.preparer_donnees_partants(course.id)
                    self._analyse_service.analyser_course(
                        course_id=course.id,
                        version=self._analyse_service.prochaine_version(course.id),
                        partants=donnees_partants,
                        sous_risques_course=sous_risques_course,
                    )
                    nb_courses += 1
                except Exception as exc:  # noqa: BLE001 - isolation volontaire par course, même motif que CollecteService
                    # Pas seulement ValidationError/BusinessRuleError (cf. bug réel
                    # du 2026-07-11) : une erreur SQL inattendue (ex. CheckViolation
                    # avant le correctif de `calculer_score_final`) doit elle aussi
                    # rester isolée à cette course — sinon elle remonte jusqu'à la
                    # route, qui `raise` à nouveau après avoir journalisé l'échec,
                    # ce qui fait annuler (rollback) toute la transaction de la
                    # requête, y compris le `tache_repo.demarrer`/`terminer` déjà
                    # exécutés : plus aucune trace de la tentative, juste un 500
                    # opaque côté HTML, et aucune des AUTRES courses du jour n'est
                    # analysée alors qu'elles n'ont rien à voir avec l'échec.
                    erreurs.append((course.id, str(exc)))
        return RapportAnalyseJour(
            nb_courses=nb_courses, nb_erreurs=len(erreurs), nb_deja_parties=nb_deja_parties, erreurs=erreurs
        )
