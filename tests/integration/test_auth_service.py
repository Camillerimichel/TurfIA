"""Teste AuthService avec des repositories en mémoire (cf. tests/integration/fakes.py),
sans base réelle."""

import pytest

from src.core.exceptions import SecurityError
from src.core.security import hacher_mot_de_passe
from src.models.utilisateur import Role, Utilisateur
from src.services.auth_service import AuthService
from tests.integration.fakes import FakeAuditRepository, FakeUtilisateurRepository


@pytest.fixture
def repos():
    utilisateurs = FakeUtilisateurRepository()
    role = utilisateurs.seed_role(Role(nom="Administrateur"))
    utilisateur = utilisateurs.seed_utilisateur(
        Utilisateur(login="jdupont", mot_de_passe=hacher_mot_de_passe("motdepasse123"), role_id=role.id)
    )
    audit = FakeAuditRepository()
    return {"utilisateurs": utilisateurs, "audit": audit, "role": role, "utilisateur": utilisateur}


@pytest.fixture
def service(repos):
    return AuthService(repos["utilisateurs"], repos["audit"], duree_session_minutes=60)


def test_authentifier_avec_bon_mot_de_passe(service, repos):
    session = service.authentifier("jdupont", "motdepasse123")
    assert session.utilisateur.login == "jdupont"
    assert session.role.nom == "Administrateur"
    assert session.jeton
    assert any(e[1] == "connexion" and e[0] == repos["utilisateur"].id for e in repos["audit"].entrees)


def test_authentifier_avec_mauvais_mot_de_passe_leve_securityerror(service, repos):
    with pytest.raises(SecurityError):
        service.authentifier("jdupont", "mauvais-mot-de-passe")
    assert any(e[1] == "echec_connexion" for e in repos["audit"].entrees)


def test_authentifier_login_inconnu_leve_securityerror(service, repos):
    with pytest.raises(SecurityError):
        service.authentifier("inconnu", "peu-importe")
    assert any(e[1] == "echec_connexion" and e[0] is None for e in repos["audit"].entrees)


def test_authentifier_compte_inactif_leve_securityerror(repos):
    repos["utilisateurs"].utilisateurs[repos["utilisateur"].id].actif = False
    service = AuthService(repos["utilisateurs"], repos["audit"], duree_session_minutes=60)
    with pytest.raises(SecurityError):
        service.authentifier("jdupont", "motdepasse123")


def test_utilisateur_courant_avec_jeton_valide(service):
    session = service.authentifier("jdupont", "motdepasse123")
    utilisateur, role = service.utilisateur_courant(session.jeton)
    assert utilisateur.login == "jdupont"
    assert role.nom == "Administrateur"


def test_utilisateur_courant_avec_jeton_invalide_leve_securityerror(service):
    with pytest.raises(SecurityError):
        service.utilisateur_courant("jeton-invalide")


def test_deconnecter_revoque_la_session(service, repos):
    session = service.authentifier("jdupont", "motdepasse123")
    service.deconnecter(session.jeton)
    with pytest.raises(SecurityError):
        service.utilisateur_courant(session.jeton)
    assert any(e[1] == "deconnexion" for e in repos["audit"].entrees)
