"""Routes du domaine Référentiels — cf. L007 §4.1, L032.2.

Endpoint représentatif de bout en bout : route -> schéma -> repository -> base SQL,
en lecture seule (cf. audience/authentification par domaine, L007 §4.1).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from api.dependencies.auth import LECTURE, exiger_roles
from api.dependencies.db import get_referentiel_repository
from api.schemas.common import Enveloppe
from api.schemas.referentiels import DisciplineOut, HippodromeOut
from src.models.utilisateur import Utilisateur
from src.repositories.referentiel_repository import ReferentielRepository

router = APIRouter(tags=["Référentiels"])


@router.get("/hippodromes", response_model=Enveloppe[list[HippodromeOut]])
def list_hippodromes(
    repo: ReferentielRepository = Depends(get_referentiel_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*LECTURE)),
) -> Enveloppe[list[HippodromeOut]]:
    hippodromes = repo.list_hippodromes()
    return Enveloppe(data=[HippodromeOut.model_validate(h) for h in hippodromes])


@router.get("/disciplines", response_model=Enveloppe[list[DisciplineOut]])
def list_disciplines(
    repo: ReferentielRepository = Depends(get_referentiel_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*LECTURE)),
) -> Enveloppe[list[DisciplineOut]]:
    disciplines = repo.list_disciplines()
    return Enveloppe(data=[DisciplineOut.model_validate(d) for d in disciplines])
