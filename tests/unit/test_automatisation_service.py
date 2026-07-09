from datetime import date

from src.core.exceptions import ValidationError
from src.models.course import Course, Reunion
from src.services.automatisation_service import AutomatisationService
from tests.integration.fakes import FakeCourseRepository


class _PreparationBoiteuse:
    """Simule `PreparationDonneesService` : lève ValidationError pour une course
    donnée, retourne des données valides pour les autres."""

    def __init__(self, course_id_en_echec: int) -> None:
        self._course_id_en_echec = course_id_en_echec

    def preparer_donnees_partants(self, course_id: int):
        if course_id == self._course_id_en_echec:
            raise ValidationError("Aucun partant collecté.")
        return [], {}


class _AnalyseServiceFactice:
    def __init__(self) -> None:
        self.appels: list[int] = []

    def analyser_course(self, course_id, version, partants, sous_risques_course, **kwargs):
        self.appels.append(course_id)
        return object()


def _seeder_reunion_trois_courses(course_repo: FakeCourseRepository) -> list[int]:
    reunion = course_repo.create_reunion(Reunion(date=date(2026, 7, 9), hippodrome_id=1, numero=1))
    ids = []
    for numero in (1, 2, 3):
        course = course_repo.create_course(Course(reunion_id=reunion.id, numero=numero, nom=f"Course {numero}"))
        ids.append(course.id)
    return ids


def test_analyser_courses_du_jour_continue_apres_une_erreur_isolee():
    course_repo = FakeCourseRepository()
    ids_courses = _seeder_reunion_trois_courses(course_repo)
    analyse_service = _AnalyseServiceFactice()
    service = AutomatisationService(course_repo, _PreparationBoiteuse(ids_courses[1]), analyse_service)

    rapport = service.analyser_courses_du_jour(date(2026, 7, 9))

    assert rapport.nb_courses == 2
    assert rapport.nb_erreurs == 1
    assert rapport.erreurs == [(ids_courses[1], "Aucun partant collecté.")]
    assert analyse_service.appels == [ids_courses[0], ids_courses[2]]


def test_analyser_courses_du_jour_aucune_reunion():
    course_repo = FakeCourseRepository()
    analyse_service = _AnalyseServiceFactice()
    service = AutomatisationService(course_repo, _PreparationBoiteuse(-1), analyse_service)

    rapport = service.analyser_courses_du_jour(date(2026, 7, 9))

    assert rapport.nb_courses == 0
    assert rapport.nb_erreurs == 0
    assert rapport.erreurs == []
