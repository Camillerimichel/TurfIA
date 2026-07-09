"""Tests d'intégration de ConsensusPresseService — combinaison des deux
sources (Canalturf/Zone-Turf), confirmation indépendante que la course
demandée est bien le Quinté+ du jour, isolation des échecs (cf.
`src/services/consensus_presse_service.py`). Aucun accès réseau (cf. L020
§2.2) : stubs simples remplaçant CanalturfClient/ZoneTurfClient.

Les extractions HTML elles-mêmes sont déjà vérifiées contre de vraies pages
capturées dans `tests/unit/test_collecte_canalturf_mappers.py`/
`test_collecte_zoneturf_mappers.py` — ce fichier teste uniquement
l'orchestration du service (combinaison, confirmation, isolation), en
réutilisant ces mêmes fixtures réelles quand la course demandée correspond,
et du HTML minimal pour les scénarios qu'aucune des deux captures réelles ne
couvre à elle seule (ex. les deux sources confirmant la même course).
"""

from pathlib import Path

import pytest

from src.core.exceptions import ImportationError
from src.services.consensus_presse_service import ConsensusPresseService

FIXTURES = Path(__file__).parent.parent / "fixtures"


class _CanalturfStub:
    def __init__(self, html_quinte_php: str, page_course: str | None = None) -> None:
        self.html_quinte_php = html_quinte_php
        self.page_course = page_course

    def recuperer_page_quinte_du_jour(self) -> str:
        return self.html_quinte_php

    def recuperer_page_course(self, url: str) -> str:
        return self.page_course


class _ZoneTurfStub:
    def __init__(self, html_quinte: str) -> None:
        self.html_quinte = html_quinte

    def recuperer_page_quinte_du_jour(self) -> str:
        return self.html_quinte


class _ClientEnPanne:
    def recuperer_page_quinte_du_jour(self):
        raise ImportationError("Panne réseau simulée.")


# HTML Canalturf minimal (mêmes motifs que src/collecte/canalturf/mappers.py),
# utilisé uniquement pour le scénario où les deux sources doivent confirmer la
# MÊME course (R1C1) — les fixtures réelles capturées correspondent à des
# Quintés de jours différents (R1C8 vs R1C5).
_CANALTURF_QUINTE_PHP_R1C1 = (
    '<a href="https://www.canalturf.com/pronostics-PMU/2026-07-09/test/1_test.html">lien</a>'
)
_CANALTURF_COURSE_R1C1 = (
    "<table><caption>Réunion R1C1</caption></table>"
    '<div id="tab-prono-pr"><tbody><tr><td>5</td><td>2</td><td>7</td></tr></tbody></div>'
)
_ZONETURF_QUINTE_R1C1 = (
    "<html>R1 C1<table>"
    '<tr><td><strong>Synthèse Quinté de la presse</strong></td>'
    '<td class="tc">3</td><td class="tc">6</td></tr>'
    "</table></html>"
)


def test_recuperer_classements_presse_combine_les_deux_sources_quand_elles_confirment_la_meme_course():
    canalturf = _CanalturfStub(_CANALTURF_QUINTE_PHP_R1C1, _CANALTURF_COURSE_R1C1)
    zoneturf = _ZoneTurfStub(_ZONETURF_QUINTE_R1C1)
    service = ConsensusPresseService(canalturf, zoneturf)

    classements = service.recuperer_classements_presse(numero_reunion=1, numero_course=1)

    assert classements == [[5, 2, 7], [3, 6]]


def test_recuperer_classements_presse_canalturf_seul_sur_echantillon_reel():
    """cf. tests/fixtures/canalturf_quinte_php.html + canalturf_course_quinte.html
    (vrai Quinté+ R1C8, cf. test_collecte_canalturf_mappers.py)."""
    html_quinte_php = (FIXTURES / "canalturf_quinte_php.html").read_text(encoding="utf-8")
    html_course_quinte = (FIXTURES / "canalturf_course_quinte.html").read_text(encoding="utf-8")
    canalturf = _CanalturfStub(html_quinte_php, html_course_quinte)
    zoneturf = _ZoneTurfStub("<html>Pas de Quinté+ aujourd'hui</html>")
    service = ConsensusPresseService(canalturf, zoneturf)

    classements = service.recuperer_classements_presse(numero_reunion=1, numero_course=8)

    assert classements == [[15, 7, 4, 2, 11, 3, 10, 14, 5, 1]]


def test_recuperer_classements_presse_zoneturf_seul_sur_echantillon_reel():
    """cf. tests/fixtures/zoneturf_quinte.html (vrai Quinté+ R1C5, cf.
    test_collecte_zoneturf_mappers.py)."""
    canalturf = _CanalturfStub("<html>Pas de Quinté+ aujourd'hui</html>")
    html_quinte_zoneturf = (FIXTURES / "zoneturf_quinte.html").read_text(encoding="utf-8")
    zoneturf = _ZoneTurfStub(html_quinte_zoneturf)
    service = ConsensusPresseService(canalturf, zoneturf)

    classements = service.recuperer_classements_presse(numero_reunion=1, numero_course=5)

    assert classements == [[9, 8, 10, 12, 7, 13, 11, 4]]


def test_recuperer_classements_presse_vide_si_course_demandee_nest_pas_le_quinte():
    """La confirmation R{réunion}C{course} ne correspond pas -> aucune source ne
    contribue, pas une erreur (cf. `_recuperer_canalturf`/`_recuperer_zoneturf`)."""
    canalturf = _CanalturfStub(_CANALTURF_QUINTE_PHP_R1C1, _CANALTURF_COURSE_R1C1)
    zoneturf = _ZoneTurfStub(_ZONETURF_QUINTE_R1C1)
    service = ConsensusPresseService(canalturf, zoneturf)

    classements = service.recuperer_classements_presse(numero_reunion=4, numero_course=1)

    assert classements == []


def test_recuperer_classements_presse_isole_une_source_en_panne():
    """cf. `_recuperer_sans_lever` : une source en échec (réseau, structure
    inattendue) est journalisée et n'empêche jamais l'autre de contribuer."""
    canalturf = _ClientEnPanne()
    zoneturf = _ZoneTurfStub(_ZONETURF_QUINTE_R1C1)
    service = ConsensusPresseService(canalturf, zoneturf)

    classements = service.recuperer_classements_presse(numero_reunion=1, numero_course=1)

    assert classements == [[3, 6]]


def test_recuperer_classements_presse_aucune_source_ne_repond():
    canalturf = _CanalturfStub("<html>Pas de Quinté+ aujourd'hui</html>")
    zoneturf = _ZoneTurfStub("<html>Pas de Quinté+ aujourd'hui</html>")
    service = ConsensusPresseService(canalturf, zoneturf)

    assert service.recuperer_classements_presse(numero_reunion=1, numero_course=1) == []
