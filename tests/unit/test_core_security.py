from src.core.security import (
    generer_jeton,
    hacher_jeton,
    hacher_mot_de_passe,
    verifier_mot_de_passe,
)


def test_hacher_mot_de_passe_ne_stocke_jamais_le_clair():
    hache = hacher_mot_de_passe("secret123")
    assert hache != "secret123"


def test_verifier_mot_de_passe_correct():
    hache = hacher_mot_de_passe("secret123")
    assert verifier_mot_de_passe("secret123", hache) is True


def test_verifier_mot_de_passe_incorrect():
    hache = hacher_mot_de_passe("secret123")
    assert verifier_mot_de_passe("autre-mot-de-passe", hache) is False


def test_generer_jeton_est_aleatoire():
    assert generer_jeton() != generer_jeton()


def test_hacher_jeton_deterministe():
    jeton = generer_jeton()
    assert hacher_jeton(jeton) == hacher_jeton(jeton)


def test_hacher_jeton_ne_reproduit_pas_le_jeton_en_clair():
    jeton = generer_jeton()
    assert hacher_jeton(jeton) != jeton
