"""Routes du domaine Administration/Système — cf. L007 §4.5, L032.1 §10."""

from __future__ import annotations

from fastapi import APIRouter

from api.schemas.common import Enveloppe
from api.schemas.system import SanteReponse, VersionReponse

router = APIRouter(prefix="/system", tags=["Système"])

APP_VERSION = "0.1.0"


@router.get("/health", response_model=Enveloppe[SanteReponse])
def health() -> Enveloppe[SanteReponse]:
    return Enveloppe(data=SanteReponse())


@router.get("/version", response_model=Enveloppe[VersionReponse])
def version() -> Enveloppe[VersionReponse]:
    return Enveloppe(data=VersionReponse(version=APP_VERSION))
