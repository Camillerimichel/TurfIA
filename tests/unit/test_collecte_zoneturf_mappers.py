from pathlib import Path

import pytest

from src.collecte.zoneturf.mappers import extraire_numero_reunion_course, extraire_synthese_presse
from src.core.exceptions import ImportationError

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


@pytest.fixture
def html_quinte():
    return (FIXTURES / "zoneturf_quinte.html").read_text(encoding="utf-8")


def test_extraire_numero_reunion_course_depuis_echantillon_reel(html_quinte):
    assert extraire_numero_reunion_course(html_quinte) == (1, 5)


def test_extraire_numero_reunion_course_absent():
    assert extraire_numero_reunion_course("<html><body>Pas de Quinté+ aujourd'hui</body></html>") is None


def test_extraire_synthese_presse_depuis_echantillon_reel(html_quinte):
    assert extraire_synthese_presse(html_quinte) == [9, 8, 10, 12, 7, 13, 11, 4]


def test_extraire_synthese_presse_absente():
    html = "<html><body><table><tr><td>Bilto</td><td class='tc'>8</td></tr></table></body></html>"
    assert extraire_synthese_presse(html) is None


def test_extraire_synthese_presse_leve_si_ligne_illisible():
    html = "<tr><td><strong>Synthèse Quinté de la presse</strong></td></tr>"
    with pytest.raises(ImportationError):
        extraire_synthese_presse(html)
