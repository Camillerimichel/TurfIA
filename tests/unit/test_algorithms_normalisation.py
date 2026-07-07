from src.algorithms.normalisation import normaliser


def test_normaliser_cas_simple():
    assert normaliser(75, 0, 100) == 75.0


def test_normaliser_inverse():
    assert normaliser(75, 0, 100, inverse=True) == 25.0


def test_normaliser_bornes_identiques_retourne_valeur_neutre():
    assert normaliser(5, 5, 5) == 50.0


def test_normaliser_clamp_superieur():
    assert normaliser(150, 0, 100) == 100.0


def test_normaliser_clamp_inferieur():
    assert normaliser(-50, 0, 100) == 0.0
