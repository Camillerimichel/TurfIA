import pytest

from src.algorithms.risque import ajuster_budget_selon_risque, calculer_risque, interpreter_risque


def test_calculer_risque_moyenne_ponderee():
    assert calculer_risque({"a": 100, "b": 0}, {"a": 1, "b": 1}) == 50.0


@pytest.mark.parametrize(
    "risque, libelle_attendu",
    [
        (0, "Très faible"),
        (25, "Très faible"),
        (26, "Faible"),
        (50, "Faible"),
        (51, "Moyen"),
        (75, "Moyen"),
        (76, "Élevé"),
        (100, "Élevé"),
    ],
)
def test_interpreter_risque(risque, libelle_attendu):
    assert interpreter_risque(risque) == libelle_attendu


def test_ajuster_budget_reduit_si_risque_eleve():
    assert ajuster_budget_selon_risque(100.0, risque=80, seuil_reduction=75, facteur_reduction=0.5) == 50.0


def test_ajuster_budget_inchange_si_risque_sous_le_seuil():
    assert ajuster_budget_selon_risque(100.0, risque=50, seuil_reduction=75) == 100.0
