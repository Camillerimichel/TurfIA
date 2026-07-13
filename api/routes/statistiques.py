"""Routes du domaine Statistiques — cf. L007 §4.5, L030.4.

Lecture seule : ces tables sont alimentées exclusivement par
`scripts/calculer_statistiques.py` (cf. PROJECT_STATE.md), jamais via l'API.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from api.dependencies.auth import LECTURE, exiger_roles
from api.dependencies.db import get_statistique_repository
from api.schemas.common import Enveloppe
from api.schemas.statistiques import (
    StatistiqueDisciplineOut,
    StatistiqueGlobaleJourOut,
    StatistiqueGlobaleOut,
    StatistiqueGlobaleParJourOut,
    StatistiqueGlobaleTotalOut,
    StatistiqueHippodromeOut,
    StatistiqueModeleOut,
    StatistiquePariOut,
    StatistiqueScoreOut,
)
from src.models.utilisateur import Utilisateur
from src.repositories.statistique_repository import StatistiqueRepository

router = APIRouter(prefix="/statistiques", tags=["Statistiques"])


@router.get("/globale", response_model=Enveloppe[list[StatistiqueGlobaleOut]])
def list_globale(
    repo: StatistiqueRepository = Depends(get_statistique_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*LECTURE)),
) -> Enveloppe[list[StatistiqueGlobaleOut]]:
    return Enveloppe(data=[StatistiqueGlobaleOut.model_validate(s) for s in repo.list_globale()])


@router.get("/globale/jours", response_model=Enveloppe[StatistiqueGlobaleParJourOut])
def globale_par_jour(
    repo: StatistiqueRepository = Depends(get_statistique_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*LECTURE)),
) -> Enveloppe[StatistiqueGlobaleParJourOut]:
    """Détail par jour de course (`reunion.date`) du bloc "Globale" + une
    ligne de consolidation totale — cf. retour utilisateur 2026-07-12
    (tableau segmenté par jour + graphique barre/courbe des gains/pertes).
    Calculé à la demande (comme `calculer_globale`), jamais persisté."""
    donnees = StatistiqueGlobaleParJourOut(
        jours=[StatistiqueGlobaleJourOut.model_validate(j) for j in repo.calculer_globale_par_jour()],
        total=StatistiqueGlobaleTotalOut.model_validate(repo.calculer_globale()),
    )
    return Enveloppe(data=donnees)


@router.get("/scores", response_model=Enveloppe[list[StatistiqueScoreOut]])
def list_scores(
    repo: StatistiqueRepository = Depends(get_statistique_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*LECTURE)),
) -> Enveloppe[list[StatistiqueScoreOut]]:
    return Enveloppe(data=[StatistiqueScoreOut.model_validate(s) for s in repo.list_scores()])


@router.get("/hippodromes", response_model=Enveloppe[list[StatistiqueHippodromeOut]])
def list_hippodromes(
    repo: StatistiqueRepository = Depends(get_statistique_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*LECTURE)),
) -> Enveloppe[list[StatistiqueHippodromeOut]]:
    return Enveloppe(data=[StatistiqueHippodromeOut.model_validate(s) for s in repo.list_hippodromes()])


@router.get("/disciplines", response_model=Enveloppe[list[StatistiqueDisciplineOut]])
def list_disciplines(
    repo: StatistiqueRepository = Depends(get_statistique_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*LECTURE)),
) -> Enveloppe[list[StatistiqueDisciplineOut]]:
    return Enveloppe(data=[StatistiqueDisciplineOut.model_validate(s) for s in repo.list_disciplines()])


@router.get("/paris", response_model=Enveloppe[list[StatistiquePariOut]])
def list_paris(
    repo: StatistiqueRepository = Depends(get_statistique_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*LECTURE)),
) -> Enveloppe[list[StatistiquePariOut]]:
    return Enveloppe(data=[StatistiquePariOut.model_validate(s) for s in repo.list_paris()])


@router.get("/modeles", response_model=Enveloppe[list[StatistiqueModeleOut]])
def list_modeles(
    repo: StatistiqueRepository = Depends(get_statistique_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*LECTURE)),
) -> Enveloppe[list[StatistiqueModeleOut]]:
    return Enveloppe(data=[StatistiqueModeleOut.model_validate(s) for s in repo.list_modeles()])
