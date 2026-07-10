"""Route du module Historique — cf. L018 §8.

Recherche transversale en lecture seule sur analyses/paris/ROI, accessible à
tous les rôles authentifiés (cf. L018 §8, pas réservé aux administrateurs).
"""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query

from api.dependencies.auth import LECTURE, exiger_roles
from api.dependencies.db import get_historique_repository
from api.schemas.common import Enveloppe
from api.schemas.historique import HistoriqueLigneOut
from src.models.historique import HistoriqueFiltres
from src.models.utilisateur import Utilisateur
from src.repositories.historique_repository import HistoriqueRepository

router = APIRouter(prefix="/historique", tags=["Historique"])


@router.get("", response_model=Enveloppe[list[HistoriqueLigneOut]])
def rechercher_historique(
    date_debut: date | None = None,
    date_fin: date | None = None,
    hippodrome_id: int | None = None,
    type_pari: str | None = None,
    decisions: list[str] | None = Query(None),
    limite: int = 200,
    repo: HistoriqueRepository = Depends(get_historique_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*LECTURE)),
) -> Enveloppe[list[HistoriqueLigneOut]]:
    filtres = HistoriqueFiltres(
        date_debut=date_debut,
        date_fin=date_fin,
        hippodrome_id=hippodrome_id,
        type_pari=type_pari,
        decisions=decisions,
        limite=limite,
    )
    return Enveloppe(data=[HistoriqueLigneOut.model_validate(l) for l in repo.rechercher(filtres)])
