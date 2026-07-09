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
from datetime import date

from src.core.exceptions import ValidationError
from src.repositories.course_repository import CourseRepository
from src.services.analyse_service import AnalyseService
from src.services.preparation_service import PreparationDonneesService


@dataclass(frozen=True)
class RapportAnalyseJour:
    nb_courses: int
    nb_erreurs: int
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

    def analyser_courses_du_jour(self, jour: date, version: int = 1) -> RapportAnalyseJour:
        """Relance `preparer_donnees_partants` + `analyser_course` pour chaque
        course des réunions de `jour` (même enchaînement que `POST
        /courses/{id}/analyses/auto`, une course à la fois). Une course en
        erreur (`ValidationError` — ex. partants sans cote collectée) n'interrompt
        pas les autres, même logique que `scripts/rejouer_versions.py`."""
        nb_courses = 0
        erreurs: list[tuple[int, str]] = []
        for reunion in self._courses.list_reunions_by_date(jour):
            for course in self._courses.list_courses_by_reunion(reunion.id):
                try:
                    donnees_partants, sous_risques_course = self._preparation.preparer_donnees_partants(course.id)
                    self._analyse_service.analyser_course(
                        course_id=course.id,
                        version=version,
                        partants=donnees_partants,
                        sous_risques_course=sous_risques_course,
                    )
                    nb_courses += 1
                except ValidationError as exc:
                    erreurs.append((course.id, str(exc)))
        return RapportAnalyseJour(nb_courses=nb_courses, nb_erreurs=len(erreurs), erreurs=erreurs)
