from src.algorithms.controle_roi import calculer_gains_simple_gagnant


def test_gains_pari_gagnant():
    gains = calculer_gains_simple_gagnant(
        mise=10.0, numero_joue="4", combinaison_gagnante="4", dividende_pour_un_euro=1.4, rembourse=False
    )
    assert gains == 14.0


def test_gains_pari_perdant():
    gains = calculer_gains_simple_gagnant(
        mise=10.0, numero_joue="4", combinaison_gagnante="7", dividende_pour_un_euro=1.4, rembourse=False
    )
    assert gains == 0.0


def test_gains_pari_rembourse():
    gains = calculer_gains_simple_gagnant(
        mise=10.0, numero_joue="4", combinaison_gagnante="", dividende_pour_un_euro=0.0, rembourse=True
    )
    assert gains == 10.0
