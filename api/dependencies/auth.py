"""Dépendances FastAPI d'authentification/autorisation — cf. L021 §3, §4."""

from __future__ import annotations

from fastapi import Depends, Header, HTTPException

from api.dependencies.services import get_auth_service
from src.core.exceptions import SecurityError
from src.models.utilisateur import Role, Utilisateur
from src.services.auth_service import AuthService

# Matrice rôle/opération (cf. L021 §4.1, PROJECT_STATE.md) :
# - LECTURE : les 4 rôles couvrent toute lecture (Consultation = lecture seule).
# - DECLENCHEMENT_ANALYSE : lecture + déclenchement d'une analyse.
# - ECRITURE_DONNEES : création/correction/suppression de données (référentiels,
#   courses, partants, résultats, cotes).
# - ADMINISTRATION : consultation de l'audit (expose les actions de tous les
#   utilisateurs, pas seulement les siennes, cf. GET /audit).
LECTURE = ("Administrateur", "Analyste", "Consultation", "Automatisation")
DECLENCHEMENT_ANALYSE = ("Administrateur", "Analyste", "Automatisation")
ECRITURE_DONNEES = ("Administrateur", "Automatisation")
ADMINISTRATION = ("Administrateur",)


def extraire_jeton(authorization: str | None) -> str:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentification requise (en-tête Authorization: Bearer <jeton>).")
    jeton = authorization.removeprefix("Bearer ").strip()
    if not jeton:
        raise HTTPException(status_code=401, detail="Jeton manquant.")
    return jeton


def get_utilisateur_courant(
    authorization: str | None = Header(default=None),
    auth_service: AuthService = Depends(get_auth_service),
) -> tuple[Utilisateur, Role]:
    jeton = extraire_jeton(authorization)
    try:
        return auth_service.utilisateur_courant(jeton)
    except SecurityError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


def exiger_roles(*roles_autorises: str):
    """Dépendance factory : 403 si le rôle de l'utilisateur authentifié n'est pas
    dans `roles_autorises` (cf. L021 §4, RBAC)."""

    def dependance(utilisateur_role: tuple[Utilisateur, Role] = Depends(get_utilisateur_courant)) -> Utilisateur:
        utilisateur, role = utilisateur_role
        if role.nom not in roles_autorises:
            raise HTTPException(status_code=403, detail=f"Rôle '{role.nom}' non autorisé pour cette opération.")
        return utilisateur

    return dependance
