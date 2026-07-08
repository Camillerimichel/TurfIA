import pytest
from fastapi import HTTPException

from api.dependencies.auth import exiger_roles, extraire_jeton
from src.models.utilisateur import Role, Utilisateur


def _utilisateur_avec_role(nom_role: str) -> tuple[Utilisateur, Role]:
    role = Role(id=1, nom=nom_role)
    utilisateur = Utilisateur(id=1, login="test", mot_de_passe="", role_id=1)
    return utilisateur, role


def test_exiger_roles_autorise_un_role_valide():
    dependance = exiger_roles("Administrateur", "Analyste")
    utilisateur_role = _utilisateur_avec_role("Analyste")
    resultat = dependance(utilisateur_role)
    assert resultat.login == "test"


def test_exiger_roles_refuse_un_role_non_autorise():
    dependance = exiger_roles("Administrateur")
    utilisateur_role = _utilisateur_avec_role("Consultation")
    with pytest.raises(HTTPException) as exc_info:
        dependance(utilisateur_role)
    assert exc_info.value.status_code == 403


def test_extraire_jeton_absent_leve_401():
    with pytest.raises(HTTPException) as exc_info:
        extraire_jeton(None)
    assert exc_info.value.status_code == 401


def test_extraire_jeton_mal_forme_leve_401():
    with pytest.raises(HTTPException) as exc_info:
        extraire_jeton("Basic abc123")
    assert exc_info.value.status_code == 401


def test_extraire_jeton_valide():
    assert extraire_jeton("Bearer mon-jeton") == "mon-jeton"
