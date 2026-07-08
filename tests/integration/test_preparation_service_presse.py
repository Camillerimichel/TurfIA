"""Vérifie le branchement du consensus presse dans PreparationDonneesService — le
contrat public de l'API (`AnalysePartantOut`) n'expose que le score agrégé, pas les
sous-scores bruts, donc ce test porte directement sur le service (cf. plan de
collecte Canalturf) plutôt que sur la réponse HTTP.
"""

from datetime import date

from src.models.course import Cheval, Course, Partant, Reunion
from src.services.preparation_service import PreparationDonneesService
from tests.integration.fakes import FakeConsensusPresseService, FakeCourseRepository


def _preparer_course_avec_partants(course_repo: FakeCourseRepository) -> Course:
    reunion = course_repo.create_reunion(Reunion(date=date(2026, 7, 7), hippodrome_id=1, numero=1))
    course = course_repo.create_course(Course(reunion_id=reunion.id, numero=8, nom="Prix Test"))
    for i, nom in enumerate(("Cheval A", "Cheval B", "Cheval C"), start=1):
        cheval = course_repo.create_cheval(Cheval(nom=nom))
        partant = course_repo.create_partant(Partant(course_id=course.id, cheval_id=cheval.id, numero=i))
        course_repo.cotes[partant.id] = 5.0
    return course


def test_presse_ajoutee_quand_une_source_repond():
    course_repo = FakeCourseRepository()
    course = _preparer_course_avec_partants(course_repo)
    presse = FakeConsensusPresseService(classements=[[2, 1, 3]])
    service = PreparationDonneesService(course_repo, presse)

    donnees_partants, _ = service.preparer_donnees_partants(course.id)

    assert all("presse" in dp.sous_scores for dp in donnees_partants)


def test_presse_combine_deux_sources_quand_les_deux_repondent():
    course_repo = FakeCourseRepository()
    course = _preparer_course_avec_partants(course_repo)
    presse = FakeConsensusPresseService(classements=[[2, 1, 3], [1, 2, 3]])
    service = PreparationDonneesService(course_repo, presse)

    donnees_partants, _ = service.preparer_donnees_partants(course.id)

    assert all("presse" in dp.sous_scores for dp in donnees_partants)


def test_presse_absente_quand_aucune_source_ne_repond():
    course_repo = FakeCourseRepository()
    course = _preparer_course_avec_partants(course_repo)
    presse = FakeConsensusPresseService(classements=[])  # aucune source n'a confirmé le Quinté+ du jour
    service = PreparationDonneesService(course_repo, presse)

    donnees_partants, _ = service.preparer_donnees_partants(course.id)

    assert all("presse" not in dp.sous_scores for dp in donnees_partants)


def test_presse_absente_sans_service_configure():
    course_repo = FakeCourseRepository()
    course = _preparer_course_avec_partants(course_repo)
    service = PreparationDonneesService(course_repo)  # pas de service presse (comportement par défaut)

    donnees_partants, _ = service.preparer_donnees_partants(course.id)

    assert all("presse" not in dp.sous_scores for dp in donnees_partants)
