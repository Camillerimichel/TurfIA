"""Route du domaine Audit — cf. L021 §13, L030.5.

Lecture seule, réservée à Administrateur : la table `audit` expose les actions
de tous les utilisateurs, pas seulement celles de l'appelant.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from api.dependencies.auth import ADMINISTRATION, exiger_roles
from api.dependencies.db import get_audit_repository
from api.schemas.audit import AuditOut
from api.schemas.common import Enveloppe
from src.models.utilisateur import Utilisateur
from src.repositories.audit_repository import AuditRepository

router = APIRouter(tags=["Audit"])


@router.get("/audit", response_model=Enveloppe[list[AuditOut]])
def list_audit(
    limite: int = 200,
    repo: AuditRepository = Depends(get_audit_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*ADMINISTRATION)),
) -> Enveloppe[list[AuditOut]]:
    return Enveloppe(data=[AuditOut.model_validate(a) for a in repo.lister(limite)])
