import pytest

from src.algorithms.classement import (
    PartantClasse,
    calculer_budget,
    calculer_score_final,
    categoriser,
    construire_paris,
    trier_partants,
    verifier_absence_martingale,
)
from src.core.exceptions import BusinessRuleError


def _partant(partant_id, score_final, rang, categorie, roi_theorique=5.0):
    p = PartantClasse(
        partant_id, score_turfia=score_final, score_final=score_final, risque=10, roi_theorique=roi_theorique,
        consensus=50, evolution_cote=0, value_bet=False, rang=rang,
    )
    p.categorie = categorie
    return p


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


def test_categoriser_deuxieme_rang_avec_score_eleve_est_aussi_base():
    partant = PartantClasse(2, score_turfia=88, score_final=88, risque=10, roi_theorique=8, consensus=70, evolution_cote=0, value_bet=False, rang=2)
    assert categoriser(partant) == "Base"


def test_categoriser_troisieme_rang_ne_peut_pas_etre_base():
    partant = PartantClasse(3, score_turfia=90, score_final=90, risque=10, roi_theorique=8, consensus=70, evolution_cote=0, value_bet=False, rang=3)
    assert categoriser(partant) == "Chance régulière"


def test_construire_paris_sans_budget_ne_construit_rien():
    partants = [_partant(1, 90, 1, "Base")]
    assert construire_paris(partants, budget=0) == []


def test_construire_paris_seulement_base_n1_genere_gagnant_et_place():
    partants = [_partant(1, 90, 1, "Base"), _partant(2, 60, 2, "Tocard")]
    paris = construire_paris(partants, budget=10.0)
    types = {type_pari for type_pari, _, _ in paris}
    assert types == {"Simple Gagnant", "Simple Placé"}
    mise_totale = sum(mise for _, _, mise in paris)
    assert mise_totale == pytest.approx(10.0, abs=0.05)


def test_construire_paris_avec_toutes_les_categories_disponibles():
    partants = [
        _partant(1, 90, 1, "Base"),
        _partant(2, 88, 2, "Base"),
        _partant(3, 75, 3, "Chance régulière"),
        _partant(4, 72, 4, "Chance régulière"),
    ]
    paris = construire_paris(partants, budget=50.0)
    types = [type_pari for type_pari, _, _ in paris]
    assert set(types) == {"Simple Gagnant", "Simple Placé", "Couplé Gagnant", "Couplé Placé", "2 sur 4"}
    # Simple Placé génère 2 paris distincts (Base n°1 et Chance régulière n°1)
    assert types.count("Simple Placé") == 2
    mise_totale = sum(mise for _, _, mise in paris)
    assert mise_totale == pytest.approx(50.0, abs=0.10)

    couple_gagnant = next((chevaux, mise) for type_pari, chevaux, mise in paris if type_pari == "Couplé Gagnant")
    assert {c.partant_id for c in couple_gagnant[0]} == {1, 2}

    deux_sur_quatre = next(chevaux for type_pari, chevaux, _ in paris if type_pari == "2 sur 4")
    assert {c.partant_id for c in deux_sur_quatre} == {1, 2, 3, 4}


def test_construire_paris_combinaison_utilise_partant_id():
    partants = [_partant(1, 90, 1, "Base"), _partant(2, 88, 2, "Base")]
    paris = construire_paris(partants, budget=20.0)
    couple = next(chevaux for type_pari, chevaux, _ in paris if type_pari == "Couplé Gagnant")
    assert [c.partant_id for c in couple] == [1, 2]
