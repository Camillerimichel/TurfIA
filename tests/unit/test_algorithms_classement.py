import pytest

from src.algorithms.classement import (
    PartantClasse,
    calculer_budget,
    calculer_score_final,
    categoriser,
    trier_partants,
    verifier_absence_martingale,
)
from src.core.exceptions import BusinessRuleError


def test_calculer_score_final_avec_value_bet():
    assert calculer_score_final(70, value_bet=True, risque=20, bonus_value_bet=5, malus_risque=0.2) == 71.0


def test_calculer_score_final_sans_value_bet():
    assert calculer_score_final(70, value_bet=False, risque=20, malus_risque=0.2) == 66.0


def test_trier_partants_assigne_le_rang_par_score_final_decroissant():
    partants = [
        PartantClasse(1, score_turfia=60, score_final=60, risque=20, roi_theorique=5, consensus=40, evolution_cote=0, value_bet=False),
        PartantClasse(2, score_turfia=80, score_final=80, risque=20, roi_theorique=10, consensus=60, evolution_cote=0, value_bet=False),
    ]
    classes = trier_partants(partants)
    assert [p.partant_id for p in classes] == [2, 1]
    assert classes[0].rang == 1
    assert classes[1].rang == 2


def test_calculer_budget_paliers():
    assert calculer_budget(50) == 0.0
    assert calculer_budget(60) == 10.0
    assert calculer_budget(75) == 25.0
    assert calculer_budget(90) == 50.0


def test_verifier_absence_martingale_refuse_augmentation_apres_perte():
    with pytest.raises(BusinessRuleError):
        verifier_absence_martingale(budget_propose=20, budget_precedent=10, perte_precedente=True)


def test_verifier_absence_martingale_autorise_budget_stable_ou_reduit():
    verifier_absence_martingale(budget_propose=10, budget_precedent=10, perte_precedente=True)
    verifier_absence_martingale(budget_propose=20, budget_precedent=10, perte_precedente=False)


def test_categoriser_tete_de_classement_avec_score_eleve():
    partant = PartantClasse(1, score_turfia=90, score_final=90, risque=10, roi_theorique=10, consensus=80, evolution_cote=0, value_bet=False, rang=1)
    assert categoriser(partant) == "Base"
