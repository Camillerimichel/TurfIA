"""Teste ControleRoiService avec des repositories/client en mémoire (cf.
tests/integration/fakes.py), sans base réelle ni accès réseau."""

from datetime import date

import pytest

from src.models.analyse import Analyse, Pari
from src.models.course import Cheval, Course, Partant, Reunion
from src.services.controle_roi_service import ControleRoiService
from tests.integration.fakes import FakeAnalyseRepository, FakeCourseRepository, FakePMUClient

RAPPORT_GAGNANT = [{"typePari": "SIMPLE_GAGNANT", "rembourse": False, "rapports": [{"combinaison": "4", "dividendePourUnEuro": 140}]}]

RAPPORT_COUPLE_GAGNANT = [
    {"typePari": "COUPLE_GAGNANT", "rembourse": False, "rapports": [{"combinaison": "5-3", "dividendePourUnEuro": 6760}]}
]

RAPPORT_DEUX_SUR_QUATRE = [
    {
        "typePari": "DEUX_SUR_QUATRE",
        "rembourse": False,
        "rapports": [
            {"combinaison": "5-3", "dividendePourUnEuro": 1030},
            {"combinaison": "5-7", "dividendePourUnEuro": 1030},
            {"combinaison": "5-10", "dividendePourUnEuro": 1030},
            {"combinaison": "3-7", "dividendePourUnEuro": 1030},
            {"combinaison": "3-10", "dividendePourUnEuro": 1030},
            {"combinaison": "7-10", "dividendePourUnEuro": 1030},
        ],
    }
]

RAPPORT_QUINTE = [
    {
        "typePari": "QUINTE_PLUS",
        "rembourse": False,
        "rapports": [
            {"libelle": "Quinté+ Ordre", "combinaison": "5-3-7-10-2", "dividendePourUnEuro": 6317570},
            {"libelle": "Quinté+ Désordre", "combinaison": "5-3-7-10-2", "dividendePourUnEuro": 52640},
            {"libelle": "Bonus 4sur5", "combinaison": "5-3-7-10", "dividendePourUnEuro": 600},
            {"libelle": "Bonus 4sur5", "combinaison": "5-3-7-2", "dividendePourUnEuro": 600},
            {"libelle": "Bonus 4sur5", "combinaison": "5-3-10-2", "dividendePourUnEuro": 600},
            {"libelle": "Bonus 4sur5", "combinaison": "5-7-10-2", "dividendePourUnEuro": 600},
            {"libelle": "Bonus 4sur5", "combinaison": "3-7-10-2", "dividendePourUnEuro": 600},
            {"libelle": "Bonus 3", "combinaison": "5-3-7", "dividendePourUnEuro": 440},
        ],
    }
]


def _preparer_course(course_repo: FakeCourseRepository, numero_partant_choisi: int = 4) -> tuple[Course, Partant]:
    reunion = course_repo.create_reunion(Reunion(date=date(2026, 7, 7), hippodrome_id=1, numero=1))
    course = course_repo.create_course(Course(reunion_id=reunion.id, numero=1, nom="Prix Test"))
    cheval = course_repo.create_cheval(Cheval(nom="Cheval Choisi"))
    partant = course_repo.create_partant(Partant(course_id=course.id, cheval_id=cheval.id, numero=numero_partant_choisi))
    return course, partant


def _preparer_deux_partants(course_repo: FakeCourseRepository, numero_1: int, numero_2: int):
    reunion = course_repo.create_reunion(Reunion(date=date(2026, 7, 7), hippodrome_id=1, numero=1))
    course = course_repo.create_course(Course(reunion_id=reunion.id, numero=1, nom="Prix Test"))
    cheval_1 = course_repo.create_cheval(Cheval(nom="Cheval Un"))
    cheval_2 = course_repo.create_cheval(Cheval(nom="Cheval Deux"))
    partant_1 = course_repo.create_partant(Partant(course_id=course.id, cheval_id=cheval_1.id, numero=numero_1))
    partant_2 = course_repo.create_partant(Partant(course_id=course.id, cheval_id=cheval_2.id, numero=numero_2))
    return course, partant_1, partant_2


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

    pari = analyse_repo.list_paris_by_analyse(controles[0].analyse_id)[0]
    detail = analyse_repo.controle_roi_paris[pari.id]
    assert detail.mise == 10.0
    assert detail.gains == 14.0
    assert detail.valide is True


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


def test_calcule_un_controle_couple_gagnant():
    course_repo = FakeCourseRepository()
    analyse_repo = FakeAnalyseRepository()
    course, partant_1, partant_2 = _preparer_deux_partants(course_repo, numero_1=5, numero_2=3)
    analyse = analyse_repo.create_analyse(Analyse(course_id=course.id, version=1, budget=1.0))
    analyse_repo.create_pari(
        Pari(
            analyse_id=analyse.id, type_pari="Couplé Gagnant",
            combinaison=f"{partant_1.id}-{partant_2.id}", mise=1.0,
        )
    )
    pmu_client = FakePMUClient(rapports_par_course={(1, 1): RAPPORT_COUPLE_GAGNANT})
    service = ControleRoiService(pmu_client, analyse_repo, course_repo)

    controles = service.calculer_controles_manquants()

    assert len(controles) == 1
    assert controles[0].gains == 67.60
    assert controles[0].valide is True


def test_calcule_un_controle_deux_sur_quatre_avec_deux_correspondances():
    course_repo = FakeCourseRepository()
    analyse_repo = FakeAnalyseRepository()
    reunion = course_repo.create_reunion(Reunion(date=date(2026, 7, 7), hippodrome_id=1, numero=1))
    course = course_repo.create_course(Course(reunion_id=reunion.id, numero=1, nom="Prix Test"))
    numeros_joues = [5, 3, 1, 2]
    partants = [
        course_repo.create_partant(
            Partant(course_id=course.id, cheval_id=course_repo.create_cheval(Cheval(nom=f"Cheval {n}")).id, numero=n)
        )
        for n in numeros_joues
    ]
    analyse = analyse_repo.create_analyse(Analyse(course_id=course.id, version=1, budget=3.0))
    analyse_repo.create_pari(
        Pari(
            analyse_id=analyse.id, type_pari="2 sur 4",
            combinaison="-".join(str(p.id) for p in partants), mise=3.0,
        )
    )
    pmu_client = FakePMUClient(rapports_par_course={(1, 1): RAPPORT_DEUX_SUR_QUATRE})
    service = ControleRoiService(pmu_client, analyse_repo, course_repo)

    controles = service.calculer_controles_manquants()

    assert len(controles) == 1
    assert controles[0].gains == pytest.approx(30.9)
    assert controles[0].valide is True


def test_pari_type_non_pris_en_charge_est_ignore():
    course_repo = FakeCourseRepository()
    analyse_repo = FakeAnalyseRepository()
    course, partant = _preparer_course(course_repo)
    analyse = analyse_repo.create_analyse(Analyse(course_id=course.id, version=1, budget=10.0))
    analyse_repo.create_pari(
        Pari(analyse_id=analyse.id, type_pari="Quinté Flexi", combinaison=str(partant.id), mise=10.0)
    )
    pmu_client = FakePMUClient(rapports_par_course={(1, 1): RAPPORT_GAGNANT})
    service = ControleRoiService(pmu_client, analyse_repo, course_repo)

    assert service.calculer_controles_manquants() == []


def test_plusieurs_types_de_pari_dans_la_meme_analyse_ont_chacun_leur_detail():
    """Reproduit le scénario du bug de régression corrigé le 2026-07-08 : une
    analyse avec plusieurs paris de types différents doit produire un
    `controle_roi_pari` distinct par pari (pas de double-comptage de l'agrégat
    analyse), condition nécessaire à un `statistique_pari` correct."""
    course_repo = FakeCourseRepository()
    analyse_repo = FakeAnalyseRepository()
    course, partant_1, partant_2 = _preparer_deux_partants(course_repo, numero_1=5, numero_2=3)
    analyse = analyse_repo.create_analyse(Analyse(course_id=course.id, version=1, budget=11.0))
    analyse_repo.create_pari(
        Pari(analyse_id=analyse.id, type_pari="Simple Gagnant", combinaison=str(partant_1.id), mise=10.0)
    )
    analyse_repo.create_pari(
        Pari(
            analyse_id=analyse.id, type_pari="Couplé Gagnant",
            combinaison=f"{partant_1.id}-{partant_2.id}", mise=1.0,
        )
    )
    pmu_client = FakePMUClient(rapports_par_course={(1, 1): [
        {"typePari": "SIMPLE_GAGNANT", "rembourse": False, "rapports": [{"combinaison": "5", "dividendePourUnEuro": 140}]},
        RAPPORT_COUPLE_GAGNANT[0],
    ]})
    service = ControleRoiService(pmu_client, analyse_repo, course_repo)

    controles = service.calculer_controles_manquants()

    assert len(controles) == 1
    assert controles[0].mise == 11.0
    assert controles[0].gains == pytest.approx(14.0 + 67.60)

    paris = analyse_repo.list_paris_by_analyse(analyse.id)
    detail_gagnant = analyse_repo.controle_roi_paris[next(p.id for p in paris if p.type_pari == "Simple Gagnant")]
    detail_couple = analyse_repo.controle_roi_paris[next(p.id for p in paris if p.type_pari == "Couplé Gagnant")]
    assert detail_gagnant.mise == 10.0 and detail_gagnant.gains == 14.0
    assert detail_couple.mise == 1.0 and detail_couple.gains == pytest.approx(67.60)


def test_calcule_un_controle_quinte_flexi_avec_champ_de_6_chevaux():
    """Sélection de 6 chevaux (n=6, Flexi) : les 5 vrais arrivants (5,3,7,10,2)
    + 1 cheval supplémentaire (9). C(6,5)=6 sous-combinaisons : 1 désordre exact
    + 5 bonus4sur5 (chacune omet un des 5 vrais arrivants pour le 9)."""
    course_repo = FakeCourseRepository()
    analyse_repo = FakeAnalyseRepository()
    reunion = course_repo.create_reunion(Reunion(date=date(2026, 7, 7), hippodrome_id=1, numero=1))
    course = course_repo.create_course(Course(reunion_id=reunion.id, numero=1, nom="Prix Test"))
    numeros_joues = [5, 3, 7, 10, 2, 9]
    partants = [
        course_repo.create_partant(
            Partant(course_id=course.id, cheval_id=course_repo.create_cheval(Cheval(nom=f"Cheval {n}")).id, numero=n)
        )
        for n in numeros_joues
    ]
    analyse = analyse_repo.create_analyse(Analyse(course_id=course.id, version=1, budget=3.0))
    analyse_repo.create_pari(
        Pari(
            analyse_id=analyse.id, type_pari="Quinté Flexi",
            combinaison="-".join(str(p.id) for p in partants), mise=3.0,
        )
    )
    pmu_client = FakePMUClient(rapports_par_course={(1, 1): RAPPORT_QUINTE})
    service = ControleRoiService(pmu_client, analyse_repo, course_repo)

    controles = service.calculer_controles_manquants()

    assert len(controles) == 1
    # mise par combinaison = 3.0 / 6 = 0.5 ; gains = 0.5*(526.40 + 5*6.0)
    assert controles[0].gains == pytest.approx(0.5 * (526.40 + 5 * 6.0))
    assert controles[0].valide is True


def test_rapport_indisponible_pour_ce_type_de_pari_est_ignore_sans_planter():
    """Une course ordinaire (non Quinté+) ne propose pas COUPLE_GAGNANT côté PMU —
    le pari doit être ignoré sans faire échouer tout le contrôle (cf. plan)."""
    course_repo = FakeCourseRepository()
    analyse_repo = FakeAnalyseRepository()
    course, partant_1, partant_2 = _preparer_deux_partants(course_repo, numero_1=5, numero_2=3)
    analyse = analyse_repo.create_analyse(Analyse(course_id=course.id, version=1, budget=1.0))
    analyse_repo.create_pari(
        Pari(
            analyse_id=analyse.id, type_pari="Couplé Gagnant",
            combinaison=f"{partant_1.id}-{partant_2.id}", mise=1.0,
        )
    )
    pmu_client = FakePMUClient(rapports_par_course={(1, 1): RAPPORT_GAGNANT})  # pas de COUPLE_GAGNANT simulé
    service = ControleRoiService(pmu_client, analyse_repo, course_repo)

    assert service.calculer_controles_manquants() == []
