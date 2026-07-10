from datetime import date, datetime

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
    def __init__(self, versions_existantes: dict[int, int] | None = None) -> None:
        self.appels: list[tuple[int, int]] = []
        self._versions_existantes = versions_existantes or {}

    def prochaine_version(self, course_id: int) -> int:
        return self._versions_existantes.get(course_id, 0) + 1

    def analyser_course(self, course_id, version, partants, sous_risques_course, **kwargs):
        self.appels.append((course_id, version))
        return object()


def _seeder_reunion_trois_courses(course_repo: FakeCourseRepository, heures_depart: dict[int, object] | None = None) -> list[int]:
    """`heures_depart` : `{numero: datetime | None}` pour surcharger l'heure de
    départ par défaut (`None` = non renseignée, jamais ignorée par `analyser_courses_du_jour`)."""
    heures_depart = heures_depart or {}
    reunion = course_repo.create_reunion(Reunion(date=date(2026, 7, 9), hippodrome_id=1, numero=1))
    ids = []
    for numero in (1, 2, 3):
        course = course_repo.create_course(
            Course(reunion_id=reunion.id, numero=numero, nom=f"Course {numero}", heure_depart=heures_depart.get(numero))
        )
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
    assert [course_id for course_id, _ in analyse_service.appels] == [ids_courses[0], ids_courses[2]]


def test_analyser_courses_du_jour_vise_toujours_la_version_suivante():
    """Chaque exécution horaire (cf. L033, scripts/rafraichir_et_analyser_jour.py)
    doit pouvoir recalculer une course déjà analysée sans jamais entrer en
    conflit de version — la décision peut donc changer d'une heure à l'autre."""
    course_repo = FakeCourseRepository()
    ids_courses = _seeder_reunion_trois_courses(course_repo)
    analyse_service = _AnalyseServiceFactice(versions_existantes={ids_courses[1]: 2})
    service = AutomatisationService(course_repo, _PreparationBoiteuse(-1), analyse_service)

    rapport = service.analyser_courses_du_jour(date(2026, 7, 9))

    assert rapport.nb_courses == 3
    assert rapport.nb_erreurs == 0
    assert rapport.nb_deja_parties == 0
    versions_par_course = dict(analyse_service.appels)
    assert versions_par_course[ids_courses[0]] == 1
    assert versions_par_course[ids_courses[1]] == 3
    assert versions_par_course[ids_courses[2]] == 1


def test_analyser_courses_du_jour_ignore_les_courses_deja_parties():
    course_repo = FakeCourseRepository()
    maintenant = datetime(2026, 7, 9, 14, 0)
    ids_courses = _seeder_reunion_trois_courses(
        course_repo,
        heures_depart={
            1: datetime(2026, 7, 9, 10, 0),  # déjà partie
            2: datetime(2026, 7, 9, 15, 0),  # pas encore partie
            # 3 : heure de départ inconnue -> jamais ignorée
        },
    )
    analyse_service = _AnalyseServiceFactice()
    service = AutomatisationService(course_repo, _PreparationBoiteuse(-1), analyse_service)

    rapport = service.analyser_courses_du_jour(date(2026, 7, 9), maintenant=maintenant)

    assert rapport.nb_courses == 2
    assert rapport.nb_erreurs == 0
    assert rapport.nb_deja_parties == 1
    assert [course_id for course_id, _ in analyse_service.appels] == [ids_courses[1], ids_courses[2]]


def test_analyser_courses_du_jour_aucune_reunion():
    course_repo = FakeCourseRepository()
    analyse_service = _AnalyseServiceFactice()
    service = AutomatisationService(course_repo, _PreparationBoiteuse(-1), analyse_service)

    rapport = service.analyser_courses_du_jour(date(2026, 7, 9))

    assert rapport.nb_courses == 0
    assert rapport.nb_erreurs == 0
    assert rapport.erreurs == []
