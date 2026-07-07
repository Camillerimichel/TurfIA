import pytest

from src.algorithms.score import calculer_score, determiner_decision
from src.core.exceptions import ValidationError


def test_calculer_score_moyenne_ponderee():
    assert calculer_score({"a": 100, "b": 0}, {"a": 1, "b": 1}) == 50.0


def test_calculer_score_rejette_valeur_hors_bornes():
    with pytest.raises(ValidationError):
        calculer_score({"a": 150})


def test_calculer_score_rejette_somme_poids_nulle():
    with pytest.raises(ValidationError):
        calculer_score({"a": 50}, {"a": 0})


@pytest.mark.parametrize(
    "score, decision_attendue",
    [
        (50, "Ne pas jouer"),
        (60, "Jeu prudent"),
        (74.9, "Jeu prudent"),
        (75, "Jeu normal"),
        (84.9, "Jeu normal"),
        (85, "Forte opportunité"),
        (95, "Forte opportunité"),
    ],
)
def test_determiner_decision_seuils(score, decision_attendue):
    assert determiner_decision(score) == decision_attendue
