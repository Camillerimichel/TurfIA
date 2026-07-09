import pytest

from src.algorithms.rejeu import agreger_resultats_rejeu


def test_agreger_resultats_rejeu_vide():
    assert agreger_resultats_rejeu([]) == (0, None, None)


def test_agreger_resultats_rejeu_tout_gagnant():
    resultats = [(10.0, 14.0, True), (5.0, 8.0, True)]
    nb_paris, roi, taux_reussite = agreger_resultats_rejeu(resultats)
    assert nb_paris == 2
    assert roi == pytest.approx(((14.0 + 8.0 - 15.0) / 15.0) * 100)
    assert taux_reussite == 100.0


def test_agreger_resultats_rejeu_tout_perdant():
    resultats = [(10.0, 0.0, False), (5.0, 0.0, False)]
    nb_paris, roi, taux_reussite = agreger_resultats_rejeu(resultats)
    assert nb_paris == 2
    assert roi == pytest.approx(-100.0)
    assert taux_reussite == 0.0


def test_agreger_resultats_rejeu_mixte():
    resultats = [(10.0, 14.0, True), (10.0, 0.0, False), (10.0, 0.0, False), (10.0, 0.0, False)]
    nb_paris, roi, taux_reussite = agreger_resultats_rejeu(resultats)
    assert nb_paris == 4
    assert roi == pytest.approx(((14.0 - 40.0) / 40.0) * 100)
    assert taux_reussite == 25.0
