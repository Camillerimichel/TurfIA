"""Tests d'intégration de l'authentification réelle — cf. L021 §3.
`client_auth_reelle` n'a pas la dépendance `get_utilisateur_courant` contournée
(contrairement au client `client` utilisé par les autres tests), pour tester le
vrai enchaînement login -> jeton -> route protégée."""

import pytest

from src.core.security import hacher_mot_de_passe
from src.models.utilisateur import Role, Utilisateur


@pytest.fixture(autouse=True)
def limiteur_login_reinitialise():
    """`api.routes.auth._limiteur_login` est un singleton de module (délibéré, cf.
    src/core/rate_limiter.py — il doit survivre entre requêtes en production) : le
    réinitialiser entre les tests évite qu'un test consomme le quota d'un autre."""
    import api.routes.auth as module_auth

    module_auth._limiteur_login = module_auth.LimiteurDebit(
        module_auth._settings.login_max_tentatives, module_auth._settings.login_fenetre_secondes
    )


def _creer_utilisateur(repos, role_nom="Administrateur", actif=True, mot_de_passe="motdepasse123"):
    role = repos["utilisateurs"].seed_role(Role(nom=role_nom))
    return repos["utilisateurs"].seed_utilisateur(
        Utilisateur(login="jdupont", mot_de_passe=hacher_mot_de_passe(mot_de_passe), role_id=role.id, actif=actif)
    )


def test_login_reussi_retourne_un_jeton(client_auth_reelle, repos):
    _creer_utilisateur(repos)
    reponse = client_auth_reelle.post("/api/v1/auth/login", json={"login": "jdupont", "mot_de_passe": "motdepasse123"})
    assert reponse.status_code == 200
    corps = reponse.json()["data"]
    assert corps["jeton"]
    assert corps["utilisateur"]["login"] == "jdupont"
    assert corps["utilisateur"]["role"] == "Administrateur"


def test_login_mot_de_passe_incorrect_retourne_401(client_auth_reelle, repos):
    _creer_utilisateur(repos)
    reponse = client_auth_reelle.post("/api/v1/auth/login", json={"login": "jdupont", "mot_de_passe": "mauvais"})
    assert reponse.status_code == 401
    assert reponse.json()["error"]["code"] == "NON_AUTHENTIFIE"


def test_login_utilisateur_inconnu_retourne_401(client_auth_reelle):
    reponse = client_auth_reelle.post("/api/v1/auth/login", json={"login": "fantome", "mot_de_passe": "peu-importe"})
    assert reponse.status_code == 401


def test_login_compte_inactif_retourne_401(client_auth_reelle, repos):
    _creer_utilisateur(repos, actif=False)
    reponse = client_auth_reelle.post("/api/v1/auth/login", json={"login": "jdupont", "mot_de_passe": "motdepasse123"})
    assert reponse.status_code == 401


def test_login_limite_le_debit(client_auth_reelle, repos):
    _creer_utilisateur(repos)
    for _ in range(5):
        client_auth_reelle.post("/api/v1/auth/login", json={"login": "jdupont", "mot_de_passe": "mauvais"})
    reponse = client_auth_reelle.post("/api/v1/auth/login", json={"login": "jdupont", "mot_de_passe": "mauvais"})
    assert reponse.status_code == 429


def test_route_protegee_sans_jeton_retourne_401(client_auth_reelle):
    reponse = client_auth_reelle.get("/api/v1/hippodromes")
    assert reponse.status_code == 401
    assert reponse.json()["error"]["code"] == "NON_AUTHENTIFIE"


def test_route_protegee_avec_jeton_valide(client_auth_reelle, repos):
    _creer_utilisateur(repos)
    jeton = client_auth_reelle.post(
        "/api/v1/auth/login", json={"login": "jdupont", "mot_de_passe": "motdepasse123"}
    ).json()["data"]["jeton"]

    reponse = client_auth_reelle.get("/api/v1/hippodromes", headers={"Authorization": f"Bearer {jeton}"})
    assert reponse.status_code == 200


def test_logout_puis_reutilisation_du_jeton_retourne_401(client_auth_reelle, repos):
    _creer_utilisateur(repos)
    jeton = client_auth_reelle.post(
        "/api/v1/auth/login", json={"login": "jdupont", "mot_de_passe": "motdepasse123"}
    ).json()["data"]["jeton"]
    entetes = {"Authorization": f"Bearer {jeton}"}

    reponse_logout = client_auth_reelle.post("/api/v1/auth/logout", headers=entetes)
    assert reponse_logout.status_code == 200

    reponse_apres = client_auth_reelle.get("/api/v1/hippodromes", headers=entetes)
    assert reponse_apres.status_code == 401
