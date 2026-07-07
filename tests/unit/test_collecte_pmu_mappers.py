import json
from pathlib import Path

import pytest

from src.collecte.pmu.mappers import (
    extraire_classement,
    extraire_cote_directe,
    extraire_etat_piste_libelle,
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


def test_mapper_discipline_code_connu():
    assert mapper_discipline_code("PLAT") == "Plat"
    assert mapper_discipline_code("ATTELE") == "Trot Attelé"


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
