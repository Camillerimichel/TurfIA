import pytest

from src.algorithms.controle_roi import calculer_gains_couple, calculer_gains_deux_sur_quatre, calculer_gains_simple


def test_gains_simple_pari_gagnant():
    gains = calculer_gains_simple(mise=10.0, numero_joue="4", dividendes_gagnants={"4": 1.4}, rembourse=False)
    assert gains == 14.0


def test_gains_simple_pari_perdant():
    gains = calculer_gains_simple(mise=10.0, numero_joue="4", dividendes_gagnants={"7": 1.4}, rembourse=False)
    assert gains == 0.0


def test_gains_simple_pari_rembourse():
    gains = calculer_gains_simple(mise=10.0, numero_joue="4", dividendes_gagnants={}, rembourse=True)
    assert gains == 10.0


def test_gains_simple_place_choisit_le_dividende_du_bon_cheval():
    dividendes = {"4": 1.05, "1": 1.10}
    assert calculer_gains_simple(mise=10.0, numero_joue="1", dividendes_gagnants=dividendes, rembourse=False) == 11.0


def test_gains_couple_pari_gagnant_ordre_indifferent():
    dividendes = {frozenset({"5", "3"}): 67.60}
    gains = calculer_gains_couple(mise=1.0, numeros_joues=frozenset({"3", "5"}), dividendes_gagnants=dividendes, rembourse=False)
    assert gains == 67.60


def test_gains_couple_pari_perdant():
    dividendes = {frozenset({"5", "3"}): 67.60}
    gains = calculer_gains_couple(mise=1.0, numeros_joues=frozenset({"5", "7"}), dividendes_gagnants=dividendes, rembourse=False)
    assert gains == 0.0


def test_gains_couple_place_plusieurs_paires_gagnantes():
    dividendes = {frozenset({"5", "3"}): 18.40, frozenset({"5", "7"}): 13.80, frozenset({"3", "7"}): 15.10}
    gains = calculer_gains_couple(mise=1.0, numeros_joues=frozenset({"7", "3"}), dividendes_gagnants=dividendes, rembourse=False)
    assert gains == 15.10


def test_gains_couple_pari_rembourse():
    assert calculer_gains_couple(mise=10.0, numeros_joues=frozenset({"5", "3"}), dividendes_gagnants={}, rembourse=True) == 10.0


def test_gains_deux_sur_quatre_avec_deux_correspondances():
    reference_top4 = frozenset({"5", "3", "7", "10"})
    gains = calculer_gains_deux_sur_quatre(
        mise=3.0, numeros_joues=frozenset({"5", "3", "1", "2"}), numeros_arrivee=reference_top4,
        dividende_pour_un_euro=10.30, rembourse=False,
    )
    assert gains == pytest.approx(30.9)


def test_gains_deux_sur_quatre_avec_une_seule_correspondance_perdant():
    reference_top4 = frozenset({"5", "3", "7", "10"})
    gains = calculer_gains_deux_sur_quatre(
        mise=3.0, numeros_joues=frozenset({"5", "1", "2", "9"}), numeros_arrivee=reference_top4,
        dividende_pour_un_euro=10.30, rembourse=False,
    )
    assert gains == 0.0


def test_gains_deux_sur_quatre_rembourse():
    assert calculer_gains_deux_sur_quatre(
        mise=3.0, numeros_joues=frozenset({"5", "3"}), numeros_arrivee=frozenset(), dividende_pour_un_euro=0.0, rembourse=True
    ) == 3.0
