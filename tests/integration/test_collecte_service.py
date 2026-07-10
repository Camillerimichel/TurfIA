"""Tests d'intégration de CollecteService — orchestration de la collecte du
programme du jour (cf. L015 §7, L023 §5.2 : l'échec d'une réunion/course
n'interrompt pas les suivantes), sur données PMU réelles échantillonnées
(aucun accès réseau, cf. L020 §2.2, `FakePMUClient`).
"""

import json
from datetime import date
from pathlib import Path

import pytest

from src.services.collecte_service import CollecteService
from tests.integration.fakes import FakeCourseRepository, FakePMUClient, FakeReferentielRepository

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def programme_echantillon():
    return json.loads((FIXTURES / "pmu_programme_echantillon.json").read_text(encoding="utf-8"))


@pytest.fixture
def participants_echantillon():
    return json.loads((FIXTURES / "pmu_participants_echantillon.json").read_text(encoding="utf-8"))


def _construire_service(programme, participants_par_course):
    pmu = FakePMUClient(programme=programme, participants_par_course=participants_par_course)
    referentiels = FakeReferentielRepository()
    courses = FakeCourseRepository()
    return CollecteService(pmu, referentiels, courses), courses, referentiels


def test_collecte_importe_reunion_courses_et_partants(programme_echantillon, participants_echantillon):
    """L'échantillon réel comporte 1 réunion (Chantilly) et 2 courses."""
    service, courses, referentiels = _construire_service(
        programme_echantillon, {(1, 1): participants_echantillon, (1, 2): participants_echantillon}
    )

    rapport = service.collecter_programme_du_jour(date(2026, 7, 7))

    assert rapport.nb_reunions == 1
    assert rapport.nb_courses == 2
    assert rapport.nb_partants == 6  # 3 participants x 2 courses
    assert rapport.erreurs == []

    reunions = list(courses.reunions.values())
    assert len(reunions) == 1
    assert reunions[0].numero == 1

    hippodromes = list(referentiels.hippodromes.values())
    assert len(hippodromes) == 1
    assert hippodromes[0].nom == "HIPPODROME DE CHANTILLY"
    assert reunions[0].hippodrome_id == hippodromes[0].id

    courses_creees = sorted(courses.courses.values(), key=lambda c: c.numero)
    assert [c.numero for c in courses_creees] == [1, 2]
    assert courses_creees[0].nom == "PRIX DU SOLEIL DE BRETAGNE"
    assert courses_creees[0].distance_id is not None
    assert courses_creees[0].surface_id is not None
    # Le Quinté+ de l'échantillon (parisEvenement) cible la course 8, absente de
    # cet échantillon réduit (2 courses) -> aucune des deux n'est marquée quinte.
    assert all(c.quinte is False for c in courses_creees)


def test_collecte_marque_quinte_la_course_visee_par_parisevenement(participants_echantillon):
    """cf. programme PMU réel : le Quinté+ est signalé par `parisEvenement`
    (codePari QUINTE_PLUS/E_QUINTE_PLUS) au niveau réunion, pas sur la course
    elle-même — Course.quinte doit refléter cette correspondance."""
    programme = {
        "programme": {
            "reunions": [
                {
                    "numOfficiel": 1,
                    "hippodrome": {"libelleLong": "HIPPODROME DE TEST"},
                    "pays": {"libelle": "FRANCE"},
                    "parisEvenement": [
                        {"codePari": "QUINTE_PLUS", "course": {"numReunion": 1, "numOrdre": 2}},
                        {"codePari": "E_QUINTE_PLUS", "course": {"numReunion": 1, "numOrdre": 2}},
                    ],
                    "courses": [
                        {
                            "numOrdre": 1, "libelle": "Course ordinaire", "discipline": "PLAT",
                            "distance": 2000, "distanceUnit": "METRE",
                        },
                        {
                            "numOrdre": 2, "libelle": "Course Quinté+", "discipline": "PLAT",
                            "distance": 2000, "distanceUnit": "METRE",
                        },
                    ],
                }
            ]
        }
    }
    service, courses, _ = _construire_service(
        programme, {(1, 1): participants_echantillon, (1, 2): participants_echantillon}
    )

    service.collecter_programme_du_jour(date(2026, 7, 10))

    courses_par_numero = {c.numero: c for c in courses.courses.values()}
    assert courses_par_numero[1].quinte is False
    assert courses_par_numero[2].quinte is True

    chevaux = {c.nom for c in courses.chevaux.values()}
    assert "MASTER MAN" in chevaux

    # Chaque cheval importé une fois par course où il apparaît (get_or_create) :
    # 3 chevaux distincts, réutilisés sur les 2 courses -> pas de doublon.
    assert len(chevaux) == 3


def test_collecte_reutilise_le_meme_hippodrome_entre_deux_reunions(programme_echantillon, participants_echantillon):
    """get_or_create_hippodrome ne doit pas dupliquer l'hippodrome si plusieurs
    réunions du jour s'y déroulent (cf. L013 §3.3 idempotence)."""
    reunion_2 = dict(programme_echantillon["programme"]["reunions"][0])
    reunion_2["numOfficiel"] = 2
    reunion_2["courses"] = []
    programme = {"programme": {"date": programme_echantillon["programme"]["date"], "reunions": [
        programme_echantillon["programme"]["reunions"][0], reunion_2,
    ]}}
    service, courses, referentiels = _construire_service(
        programme, {(1, 1): participants_echantillon, (1, 2): participants_echantillon}
    )

    rapport = service.collecter_programme_du_jour(date(2026, 7, 7))

    assert rapport.nb_reunions == 2
    assert len(referentiels.hippodromes) == 1  # même hippodrome, pas de doublon
    assert len(courses.reunions) == 2


def test_collecte_isole_une_course_en_echec_sans_interrompre_les_autres(programme_echantillon, participants_echantillon):
    """cf. L023 §5.2 : la course 1 échoue (participants manquants), la course 2
    est tout de même importée."""
    service, courses, referentiels = _construire_service(programme_echantillon, {(1, 2): participants_echantillon})

    rapport = service.collecter_programme_du_jour(date(2026, 7, 7))

    assert rapport.nb_reunions == 1
    assert rapport.nb_courses == 1  # seule la course 2 compte comme réussie
    assert rapport.nb_partants == 3
    assert len(rapport.erreurs) == 1
    assert "Course R1C1" in rapport.erreurs[0]
    # La course 1 est tout de même créée (métadonnées course connues avant l'échec
    # sur les participants) : effort maximal plutôt que tout-ou-rien par course.
    assert sorted(c.numero for c in courses.courses.values()) == [1, 2]
    assert courses.list_partants_by_course(
        next(c.id for c in courses.courses.values() if c.numero == 1)
    ) == []


def test_collecte_isole_une_reunion_en_echec_sans_interrompre_les_autres(participants_echantillon):
    """Réunion sans hippodrome -> erreur isolée (KeyError capturée), la
    réunion suivante est tout de même traitée."""
    programme_casse = {
        "programme": {
            "reunions": [
                {"numOfficiel": 1},  # pas de clé "hippodrome" -> erreur isolée
                {
                    "numOfficiel": 2,
                    "hippodrome": {"libelleLong": "HIPPODROME VALIDE"},
                    "pays": {"libelle": "FRANCE"},
                    "courses": [],
                },
            ]
        }
    }
    service, courses, referentiels = _construire_service(programme_casse, {})

    rapport = service.collecter_programme_du_jour(date(2026, 7, 7))

    assert rapport.nb_reunions == 1
    assert len(rapport.erreurs) == 1
    assert "Réunion R1" in rapport.erreurs[0]
    assert list(courses.reunions.values())[0].numero == 2


def test_collecte_programme_vide_ne_leve_pas(participants_echantillon):
    service, courses, _ = _construire_service({"programme": {"reunions": []}}, {})

    rapport = service.collecter_programme_du_jour(date(2026, 7, 7))

    assert rapport.nb_reunions == 0
    assert rapport.nb_courses == 0
    assert rapport.erreurs == []


def test_collecte_isole_une_unite_de_distance_pmu_inconnue(programme_echantillon, participants_echantillon):
    """cf. CollecteService._importer_course_et_partants : une unité de distance
    PMU non répertoriée (UNITES_DISTANCE_PMU) est une erreur isolée par course,
    jamais devinée."""
    programme_echantillon["programme"]["reunions"][0]["courses"][0]["distanceUnit"] = "COUDEE"
    service, courses, _ = _construire_service(
        programme_echantillon, {(1, 1): participants_echantillon, (1, 2): participants_echantillon}
    )

    rapport = service.collecter_programme_du_jour(date(2026, 7, 7))

    assert rapport.nb_courses == 1  # seule la course 2 réussit
    assert len(rapport.erreurs) == 1
    assert "Unité de distance PMU inconnue" in rapport.erreurs[0]


def test_collecter_resultats_course_specifique(participants_echantillon):
    """cf. bouton « Récupérer les résultats » de la fiche course (L018 §6-7) :
    une seule course peut être rafraîchie à la demande, sans attendre le
    prochain passage de la collecte horaire ni ré-importer tout le programme.
    L'échantillon réel a un `ordreArrivee` renseigné pour chaque participant
    (course déjà arrivée)."""
    from src.models.course import Course, Reunion

    pmu = FakePMUClient(participants_par_course={(3, 5): participants_echantillon})
    referentiels = FakeReferentielRepository()
    courses = FakeCourseRepository()
    reunion = courses.create_reunion(Reunion(date=date(2026, 7, 7), hippodrome_id=1, numero=3))
    course = courses.create_course(Course(reunion_id=reunion.id, numero=5, nom="Course Test"))
    service = CollecteService(pmu, referentiels, courses)

    nb_partants = service.collecter_resultats_course(course.id)

    assert nb_partants == 3
    resultats = courses.list_resultats_by_course(course.id)
    assert sorted(r.classement for r in resultats) == [2, 3, 5]


def test_collecter_resultats_course_inconnue_leve_business_rule_error():
    from src.core.exceptions import BusinessRuleError

    pmu = FakePMUClient()
    service = CollecteService(pmu, FakeReferentielRepository(), FakeCourseRepository())

    with pytest.raises(BusinessRuleError):
        service.collecter_resultats_course(999)
