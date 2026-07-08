"""Teste ControleRoiService avec des repositories/client en mémoire (cf.
tests/integration/fakes.py), sans base réelle ni accès réseau."""

from datetime import date

from src.models.analyse import Analyse, Pari
from src.models.course import Cheval, Course, Partant, Reunion
from src.services.controle_roi_service import ControleRoiService
from tests.integration.fakes import FakeAnalyseRepository, FakeCourseRepository, FakePMUClient

RAPPORT_GAGNANT = [{"typePari": "SIMPLE_GAGNANT", "rembourse": False, "rapports": [{"combinaison": "4", "dividendePourUnEuro": 140}]}]


def _preparer_course(course_repo: FakeCourseRepository, numero_partant_choisi: int = 4) -> tuple[Course, Partant]:
    reunion = course_repo.create_reunion(Reunion(date=date(2026, 7, 7), hippodrome_id=1, numero=1))
    course = course_repo.create_course(Course(reunion_id=reunion.id, numero=1, nom="Prix Test"))
    cheval = course_repo.create_cheval(Cheval(nom="Cheval Choisi"))
    partant = course_repo.create_partant(Partant(course_id=course.id, cheval_id=cheval.id, numero=numero_partant_choisi))
    return course, partant


def test_calcule_un_controle_gagnant():
    course_repo = FakeCourseRepository()
    analyse_repo = FakeAnalyseRepository()
    course, partant = _preparer_course(course_repo, numero_partant_choisi=4)
    analyse = analyse_repo.create_analyse(Analyse(course_id=course.id, version=1, budget=10.0))
    analyse_repo.create_pari(
        Pari(analyse_id=analyse.id, type_pari="Simple Gagnant", combinaison=str(partant.id), mise=10.0)
    )
    pmu_client = FakePMUClient(rapports_par_course={(1, 1): RAPPORT_GAGNANT})
    service = ControleRoiService(pmu_client, analyse_repo, course_repo)

    controles = service.calculer_controles_manquants()

    assert len(controles) == 1
    assert controles[0].mise == 10.0
    assert controles[0].gains == 14.0
    assert controles[0].profit == 4.0
    assert controles[0].valide is True


def test_calcule_un_controle_perdant():
    course_repo = FakeCourseRepository()
    analyse_repo = FakeAnalyseRepository()
    course, partant = _preparer_course(course_repo, numero_partant_choisi=7)  # ne correspond pas à la combinaison "4"
    analyse = analyse_repo.create_analyse(Analyse(course_id=course.id, version=1, budget=10.0))
    analyse_repo.create_pari(
        Pari(analyse_id=analyse.id, type_pari="Simple Gagnant", combinaison=str(partant.id), mise=10.0)
    )
    pmu_client = FakePMUClient(rapports_par_course={(1, 1): RAPPORT_GAGNANT})
    service = ControleRoiService(pmu_client, analyse_repo, course_repo)

    controles = service.calculer_controles_manquants()

    assert len(controles) == 1
    assert controles[0].gains == 0.0
    assert controles[0].valide is False


def test_analyse_sans_pari_est_ignoree():
    course_repo = FakeCourseRepository()
    analyse_repo = FakeAnalyseRepository()
    course, _ = _preparer_course(course_repo)
    analyse_repo.create_analyse(Analyse(course_id=course.id, version=1, budget=0.0))  # pas de pari créé
    pmu_client = FakePMUClient(rapports_par_course={(1, 1): RAPPORT_GAGNANT})
    service = ControleRoiService(pmu_client, analyse_repo, course_repo)

    assert service.calculer_controles_manquants() == []


def test_rapports_indisponibles_ignore_cette_analyse_sans_planter():
    course_repo = FakeCourseRepository()
    analyse_repo = FakeAnalyseRepository()
    course, partant = _preparer_course(course_repo)
    analyse = analyse_repo.create_analyse(Analyse(course_id=course.id, version=1, budget=10.0))
    analyse_repo.create_pari(
        Pari(analyse_id=analyse.id, type_pari="Simple Gagnant", combinaison=str(partant.id), mise=10.0)
    )
    pmu_client = FakePMUClient(rapports_par_course={})  # aucun rapport simulé disponible
    service = ControleRoiService(pmu_client, analyse_repo, course_repo)

    assert service.calculer_controles_manquants() == []


def test_analyse_deja_controlee_nest_pas_recalculee():
    course_repo = FakeCourseRepository()
    analyse_repo = FakeAnalyseRepository()
    course, partant = _preparer_course(course_repo)
    analyse = analyse_repo.create_analyse(Analyse(course_id=course.id, version=1, budget=10.0))
    analyse_repo.create_pari(
        Pari(analyse_id=analyse.id, type_pari="Simple Gagnant", combinaison=str(partant.id), mise=10.0)
    )
    pmu_client = FakePMUClient(rapports_par_course={(1, 1): RAPPORT_GAGNANT})
    service = ControleRoiService(pmu_client, analyse_repo, course_repo)
    service.calculer_controles_manquants()

    assert service.calculer_controles_manquants() == []
