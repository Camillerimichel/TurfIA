import json
from pathlib import Path

import pytest

from src.collecte.pmu.mappers import (
    extraire_classement,
    extraire_cote_directe,
    extraire_etat_piste_libelle,
    extraire_rapport_couple,
    extraire_rapport_deux_sur_quatre,
    extraire_rapport_quinte,
    extraire_rapport_simple,
    horodatage_depuis_epoch_ms,
    mapper_discipline_code,
    mapper_surface_code,
)
from src.core.exceptions import ImportationError

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


@pytest.fixture
def programme_echantillon():
    return json.loads((FIXTURES / "pmu_programme_echantillon.json").read_text(encoding="utf-8"))


@pytest.fixture
def participants_echantillon():
    return json.loads((FIXTURES / "pmu_participants_echantillon.json").read_text(encoding="utf-8"))


@pytest.fixture
def premiere_course(programme_echantillon):
    return programme_echantillon["programme"]["reunions"][0]["courses"][0]


@pytest.fixture
def rapports_definitifs_echantillon():
    return json.loads((FIXTURES / "pmu_rapports_definitifs_echantillon.json").read_text(encoding="utf-8"))


@pytest.fixture
def rapports_couple_2sur4_echantillon():
    return json.loads((FIXTURES / "pmu_rapports_couple_2sur4_echantillon.json").read_text(encoding="utf-8"))


@pytest.fixture
def rapports_quinte_echantillon():
    return json.loads((FIXTURES / "pmu_rapports_quinte_echantillon.json").read_text(encoding="utf-8"))


def test_mapper_discipline_code_connu():
    assert mapper_discipline_code("PLAT") == "Plat"
    assert mapper_discipline_code("ATTELE") == "Trot Attelé"


def test_mapper_discipline_code_variantes_haies_steeplechase_observees_reellement():
    """cf. réunion réelle du 2026-07-10 : PMU utilise parfois 'HAIE'/'STEEPLECHASE'
    (sans le S/le tiret) plutôt que 'HAIES'/'STEEPLE-CHASE'."""
    assert mapper_discipline_code("HAIE") == "Haies"
    assert mapper_discipline_code("HAIES") == "Haies"
    assert mapper_discipline_code("STEEPLECHASE") == "Steeple"
    assert mapper_discipline_code("STEEPLE-CHASE") == "Steeple"


def test_mapper_discipline_code_inconnu_leve_erreur():
    with pytest.raises(ImportationError):
        mapper_discipline_code("CODE_INEXISTANT")


def test_mapper_surface_code_connu():
    assert mapper_surface_code("HERBE") == "Gazon"


def test_mapper_surface_code_absent():
    assert mapper_surface_code(None) is None


def test_mapper_surface_code_inconnu_leve_erreur():
    with pytest.raises(ImportationError):
        mapper_surface_code("CODE_SURFACE_INEXISTANT")


def test_extraire_etat_piste_libelle_depuis_echantillon_reel(premiere_course):
    assert extraire_etat_piste_libelle(premiere_course) == "Bon"


def test_extraire_etat_piste_libelle_absent():
    assert extraire_etat_piste_libelle({}) is None


def test_horodatage_depuis_epoch_ms():
    dt = horodatage_depuis_epoch_ms(1783426680000)
    assert dt is not None
    assert dt.year == 2026


def test_horodatage_depuis_epoch_ms_absent():
    assert horodatage_depuis_epoch_ms(None) is None


def test_extraire_cote_directe_depuis_echantillon_reel(participants_echantillon):
    premier = participants_echantillon["participants"][0]
    assert extraire_cote_directe(premier) == 4.0


def test_extraire_cote_directe_absente():
    assert extraire_cote_directe({}) is None


def test_extraire_classement_depuis_echantillon_reel(participants_echantillon):
    premier = participants_echantillon["participants"][0]
    assert extraire_classement(premier) == 2


def test_extraire_classement_absent():
    assert extraire_classement({}) is None


def test_echantillon_reel_a_la_forme_attendue(programme_echantillon):
    reunion = programme_echantillon["programme"]["reunions"][0]
    assert reunion["hippodrome"]["libelleLong"] == "HIPPODROME DE CHANTILLY"
    assert len(reunion["courses"]) == 2


def test_extraire_rapport_simple_gagnant_depuis_echantillon_reel(rapports_definitifs_echantillon):
    dividendes, rembourse = extraire_rapport_simple(rapports_definitifs_echantillon, "SIMPLE_GAGNANT")
    assert dividendes == {"4": 1.4}
    assert rembourse is False


def test_extraire_rapport_simple_place_plusieurs_chevaux_dividendes_differents(rapports_definitifs_echantillon):
    dividendes, rembourse = extraire_rapport_simple(rapports_definitifs_echantillon, "SIMPLE_PLACE")
    assert dividendes == {"4": 1.05, "1": 1.10}
    assert rembourse is False


def test_extraire_rapport_simple_absent_leve_erreur():
    with pytest.raises(ImportationError):
        extraire_rapport_simple([{"typePari": "SIMPLE_PLACE", "rapports": []}], "SIMPLE_GAGNANT")


def test_extraire_rapport_simple_rembourse():
    rapports = [{"typePari": "SIMPLE_GAGNANT", "rembourse": True, "rapports": []}]
    assert extraire_rapport_simple(rapports, "SIMPLE_GAGNANT") == ({}, True)


def test_extraire_rapport_simple_illisible_leve_erreur():
    rapports = [{"typePari": "SIMPLE_GAGNANT", "rembourse": False, "rapports": []}]
    with pytest.raises(ImportationError):
        extraire_rapport_simple(rapports, "SIMPLE_GAGNANT")


def test_extraire_rapport_couple_gagnant_depuis_echantillon_reel(rapports_couple_2sur4_echantillon):
    dividendes, rembourse = extraire_rapport_couple(rapports_couple_2sur4_echantillon, "COUPLE_GAGNANT")
    assert dividendes == {frozenset({"5", "3"}): 67.60}
    assert rembourse is False


def test_extraire_rapport_couple_place_plusieurs_paires_depuis_echantillon_reel(rapports_couple_2sur4_echantillon):
    dividendes, rembourse = extraire_rapport_couple(rapports_couple_2sur4_echantillon, "COUPLE_PLACE")
    assert dividendes == {
        frozenset({"5", "3"}): 18.40,
        frozenset({"5", "7"}): 13.80,
        frozenset({"3", "7"}): 15.10,
    }
    assert rembourse is False


def test_extraire_rapport_couple_ignore_les_entrees_non_partant(rapports_couple_2sur4_echantillon):
    dividendes, _ = extraire_rapport_couple(rapports_couple_2sur4_echantillon, "COUPLE_GAGNANT")
    assert not any("NP" in combinaison for combinaison in dividendes)


def test_extraire_rapport_couple_absent_leve_erreur():
    with pytest.raises(ImportationError):
        extraire_rapport_couple([], "COUPLE_GAGNANT")


def test_extraire_rapport_deux_sur_quatre_depuis_echantillon_reel(rapports_couple_2sur4_echantillon):
    numeros_arrivee, dividende, rembourse = extraire_rapport_deux_sur_quatre(rapports_couple_2sur4_echantillon)
    assert numeros_arrivee == frozenset({"5", "3", "7", "10"})
    assert dividende == 10.30
    assert rembourse is False


def test_extraire_rapport_deux_sur_quatre_absent_leve_erreur():
    with pytest.raises(ImportationError):
        extraire_rapport_deux_sur_quatre([])


def test_extraire_rapport_quinte_depuis_echantillon_reel(rapports_quinte_echantillon):
    rapport = extraire_rapport_quinte(rapports_quinte_echantillon)
    assert rapport.numeros_arrivee == frozenset({"5", "3", "7", "10", "2"})
    assert rapport.dividende_desordre == pytest.approx(526.40)
    assert rapport.rembourse is False
    assert len(rapport.dividendes_bonus4) == 5
    assert rapport.dividendes_bonus4[frozenset({"5", "3", "7", "10"})] == pytest.approx(6.0)
    assert rapport.dividendes_bonus3 == {frozenset({"5", "3", "7"}): pytest.approx(4.40)}


def test_extraire_rapport_quinte_ignore_ordre(rapports_quinte_echantillon):
    # "Quinté+ Ordre" a un dividende bien plus élevé (6317570) que Désordre (52640) —
    # si le mapper le confondait avec Désordre, ce test échouerait.
    rapport = extraire_rapport_quinte(rapports_quinte_echantillon)
    assert rapport.dividende_desordre == pytest.approx(526.40)


def test_extraire_rapport_quinte_absent_leve_erreur():
    with pytest.raises(ImportationError):
        extraire_rapport_quinte([])
