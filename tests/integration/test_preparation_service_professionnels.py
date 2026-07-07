"""Vérifie le branchement des sous-scores Professionnels/Historique/Aptitude dans
PreparationDonneesService — agrégation pure sur repository (pas d'accès réseau),
cf. plan d'indicateurs Professionnels/Historique/Aptitude.
"""

from datetime import date

from src.models.course import Cheval, Course, Entraineur, Jockey, Partant, Reunion
from src.services.preparation_service import PreparationDonneesService
from tests.integration.fakes import FakeCourseRepository

HIPPODROME_ID = 1
DISTANCE_ID = 10
SURFACE_ID = 20
ETAT_PISTE_ID = 30


def _preparer_course(course_repo: FakeCourseRepository, avec_conditions: bool = True) -> Course:
    reunion = course_repo.create_reunion(Reunion(date=date(2026, 7, 7), hippodrome_id=HIPPODROME_ID, numero=1))
    course = course_repo.create_course(
        Course(
            reunion_id=reunion.id,
            numero=8,
            nom="Prix Test",
            distance_id=DISTANCE_ID if avec_conditions else None,
            surface_id=SURFACE_ID if avec_conditions else None,
            etat_piste_id=ETAT_PISTE_ID if avec_conditions else None,
        )
    )
    return course


def _ajouter_partant(course_repo, course, nom_cheval, jockey_id=None, entraineur_id=None):
    cheval = course_repo.create_cheval(Cheval(nom=nom_cheval))
    partant = course_repo.create_partant(
        Partant(
            course_id=course.id,
            cheval_id=cheval.id,
            numero=len(course_repo.partants) + 1,
            jockey_id=jockey_id,
            entraineur_id=entraineur_id,
        )
    )
    course_repo.cotes[partant.id] = 5.0
    return partant, cheval


def test_historique_toujours_present():
    course_repo = FakeCourseRepository()
    course = _preparer_course(course_repo)
    partant, _ = _ajouter_partant(course_repo, course, "Cheval A")
    service = PreparationDonneesService(course_repo)

    donnees_partants, _ = service.preparer_donnees_partants(course.id)

    assert all("historique" in dp.sous_scores for dp in donnees_partants)


def test_aptitude_absente_si_conditions_course_inconnues():
    course_repo = FakeCourseRepository()
    course = _preparer_course(course_repo, avec_conditions=False)
    _ajouter_partant(course_repo, course, "Cheval A")
    service = PreparationDonneesService(course_repo)

    donnees_partants, _ = service.preparer_donnees_partants(course.id)

    assert all("aptitude" not in dp.sous_scores for dp in donnees_partants)


def test_aptitude_presente_si_conditions_course_connues():
    course_repo = FakeCourseRepository()
    course = _preparer_course(course_repo, avec_conditions=True)
    _ajouter_partant(course_repo, course, "Cheval A")
    service = PreparationDonneesService(course_repo)

    donnees_partants, _ = service.preparer_donnees_partants(course.id)

    assert all("aptitude" in dp.sous_scores for dp in donnees_partants)


def test_professionnels_absente_sans_jockey_ni_entraineur():
    course_repo = FakeCourseRepository()
    course = _preparer_course(course_repo)
    _ajouter_partant(course_repo, course, "Cheval A")
    service = PreparationDonneesService(course_repo)

    donnees_partants, _ = service.preparer_donnees_partants(course.id)

    assert all("professionnels" not in dp.sous_scores for dp in donnees_partants)


def test_professionnels_reflete_le_taux_de_reussite_configure():
    course_repo = FakeCourseRepository()
    course = _preparer_course(course_repo)
    jockey = course_repo.create_jockey(Jockey(nom="Dupont"))
    entraineur = course_repo.create_entraineur(Entraineur(nom="Martin"))
    partant, _ = _ajouter_partant(course_repo, course, "Cheval A", jockey_id=jockey.id, entraineur_id=entraineur.id)

    # 3 victoires sur 3 courses pour le jockey, l'entraîneur et le couple -> score max.
    course_repo.performances_jockey[jockey.id] = (3, 3)
    course_repo.performances_entraineur[entraineur.id] = (3, 3)
    course_repo.performances_couple[(jockey.id, entraineur.id)] = (3, 3)

    service = PreparationDonneesService(course_repo)
    donnees_partants, _ = service.preparer_donnees_partants(course.id)

    dp = next(d for d in donnees_partants if d.partant_id == partant.id)
    assert dp.sous_scores["professionnels"] == 100.0
