import pytest

from src.algorithms.roi_theorique import (
    esperance,
    interpreter_roi,
    probabilite_turfia,
    probabilites_implicites_normalisees,
    roi_theorique,
)
from src.core.exceptions import ValidationError


def test_probabilites_implicites_normalisees_neutralise_la_marge():
    probabilites = probabilites_implicites_normalisees([2.0, 4.0])
    assert probabilites == pytest.approx([2 / 3, 1 / 3])
    assert sum(probabilites) == pytest.approx(1.0)


def test_probabilites_implicites_normalisees_rejette_cote_non_positive():
    with pytest.raises(ValidationError):
        probabilites_implicites_normalisees([2.0, 0.0])


def test_probabilite_turfia():
    assert probabilite_turfia(50, 200) == 0.25


def test_esperance():
    assert esperance(probabilite_turfia=0.25, rapport_estime=4, mise=10) == -9.0


def test_roi_theorique():
    assert roi_theorique(esperance_pari=-9.0, mise=10) == -90.0


def test_roi_theorique_rejette_mise_non_positive():
    with pytest.raises(ValidationError):
        roi_theorique(esperance_pari=5.0, mise=0)


@pytest.mark.parametrize(
    "roi, libelle_attendu",
    [
        (-5, "À éviter"),
        (0, "Faible intérêt"),
        (10, "Faible intérêt"),
        (11, "Intéressant"),
        (25, "Intéressant"),
        (26, "Très favorable"),
    ],
)
def test_interpreter_roi(roi, libelle_attendu):
    assert interpreter_roi(roi) == libelle_attendu
