from src.core.rate_limiter import LimiteurDebit


def test_autorise_sous_la_limite():
    limiteur = LimiteurDebit(max_tentatives=3, fenetre_secondes=60)
    assert limiteur.autoriser("cle") is True
    assert limiteur.autoriser("cle") is True
    assert limiteur.autoriser("cle") is True


def test_refuse_au_dela_de_la_limite():
    limiteur = LimiteurDebit(max_tentatives=2, fenetre_secondes=60)
    assert limiteur.autoriser("cle") is True
    assert limiteur.autoriser("cle") is True
    assert limiteur.autoriser("cle") is False


def test_cles_independantes():
    limiteur = LimiteurDebit(max_tentatives=1, fenetre_secondes=60)
    assert limiteur.autoriser("cle-a") is True
    assert limiteur.autoriser("cle-b") is True


def test_fenetre_glissante_reautorise_apres_expiration(monkeypatch):
    import src.core.rate_limiter as module

    instants = iter([100.0, 100.0, 200.0])
    monkeypatch.setattr(module.time, "monotonic", lambda: next(instants))

    limiteur = LimiteurDebit(max_tentatives=1, fenetre_secondes=50)
    assert limiteur.autoriser("cle") is True
    assert limiteur.autoriser("cle") is False
    assert limiteur.autoriser("cle") is True
