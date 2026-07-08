from pathlib import Path

import pytest

from src.collecte.canalturf.mappers import (
    extraire_consensus_presse,
    extraire_numero_reunion_course,
    extraire_url_quinte_du_jour,
)
from src.core.exceptions import ImportationError

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


@pytest.fixture
def html_quinte_php():
    return (FIXTURES / "canalturf_quinte_php.html").read_text(encoding="utf-8")


@pytest.fixture
def html_course_quinte():
    return (FIXTURES / "canalturf_course_quinte.html").read_text(encoding="utf-8")


@pytest.fixture
def html_course_ordinaire():
    return (FIXTURES / "canalturf_course_ordinaire.html").read_text(encoding="utf-8")


def test_extraire_url_quinte_du_jour_trouvee(html_quinte_php):
    url = extraire_url_quinte_du_jour(html_quinte_php)
    assert url == "https://www.canalturf.com/pronostics-PMU/2026-07-07/chantilly/411196_prix-le-roi-soleil.html"


def test_extraire_url_quinte_du_jour_absente():
    assert extraire_url_quinte_du_jour("<html><body>Rien ici</body></html>") is None


def test_extraire_numero_reunion_course_depuis_echantillon_reel(html_course_quinte):
    assert extraire_numero_reunion_course(html_course_quinte) == (1, 8)


def test_extraire_numero_reunion_course_page_ordinaire(html_course_ordinaire):
    assert extraire_numero_reunion_course(html_course_ordinaire) == (4, 1)


def test_extraire_numero_reunion_course_leve_si_caption_absent():
    with pytest.raises(ImportationError):
        extraire_numero_reunion_course("<html><body>Pas de caption</body></html>")


def test_extraire_numero_reunion_course_leve_si_format_inattendu():
    html = '<table><caption align="top">Un caption sans le motif attendu</caption></table>'
    with pytest.raises(ImportationError):
        extraire_numero_reunion_course(html)


def test_extraire_consensus_presse_depuis_echantillon_reel(html_course_quinte):
    classement = extraire_consensus_presse(html_course_quinte)
    assert classement == [15, 7, 4, 2, 11, 3, 10, 14, 5, 1]


def test_extraire_consensus_presse_absent_sur_course_ordinaire(html_course_ordinaire):
    assert extraire_consensus_presse(html_course_ordinaire) is None


def test_extraire_consensus_presse_leve_si_tableau_illisible():
    html = '<div id="tab-prono-pr">Bloc présent mais sans tableau</div>'
    with pytest.raises(ImportationError):
        extraire_consensus_presse(html)
