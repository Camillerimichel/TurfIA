import pytest

from src.algorithms.value_bets import calculer_ratio, calculer_valeur, est_value_bet, interpreter_niveau_value
from src.core.exceptions import ValidationError


def test_calculer_valeur():
    assert calculer_valeur(0.4, 0.3) == pytest.approx(0.1)


def test_calculer_ratio():
    assert calculer_ratio(0.4, 0.3) == pytest.approx(4 / 3)


def test_calculer_ratio_rejette_probabilite_marche_non_positive():
    with pytest.raises(ValidationError):
        calculer_ratio(0.4, 0.0)


def test_est_value_bet_conditions_reunies():
    assert est_value_bet(score_confiance=65, p_turfia=0.4, p_marche=0.3, risque=50) is True


def test_est_value_bet_score_insuffisant():
    assert est_value_bet(score_confiance=50, p_turfia=0.4, p_marche=0.3, risque=50) is False


def test_est_value_bet_risque_trop_eleve():
    assert est_value_bet(score_confiance=65, p_turfia=0.4, p_marche=0.3, risque=80) is False


@pytest.mark.parametrize(
    "ratio, niveau_attendu",
    [
        (0.9, "Aucune valeur"),
        (1.00, "Faible"),
        (1.10, "Faible"),
        (1.11, "Intéressante"),
        (1.25, "Intéressante"),
        (1.30, "Forte"),
    ],
)
def test_interpreter_niveau_value(ratio, niveau_attendu):
    assert interpreter_niveau_value(ratio) == niveau_attendu
