"""Schémas du domaine Statistiques — cf. L007 §4.5, L030.4.

Lecture seule : ces tables ne sont alimentées que par
`scripts/calculer_statistiques.py` (cf. PROJECT_STATE.md), jamais par l'API.
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class StatistiqueGlobaleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_calcul: datetime
    nb_courses: int
    nb_jouees: int
    nb_ignorees: int
    mises: float
    gains: float
    profit: float | None = None
    roi: float | None = None
    taux_reussite: float | None = None


class StatistiqueScoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    score_min: float
    score_max: float
    nb_courses: int
    nb_gagnantes: int
    roi: float | None = None
    taux_reussite: float | None = None


class StatistiqueHippodromeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hippodrome_id: int
    nb_courses: int
    mises: float
    gains: float
    profit: float | None = None
    roi: float | None = None


class StatistiqueDisciplineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    discipline_id: int
    nb_courses: int
    mises: float
    gains: float
    profit: float | None = None
    roi: float | None = None


class StatistiquePariOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type_pari: str
    nb_paris: int
    mises: float
    gains: float
    profit: float | None = None
    roi: float | None = None
    taux_reussite: float | None = None


class StatistiqueModeleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version_modele: str
    date_debut: date | None = None
    date_fin: date | None = None
    nb_courses: int
    roi: float | None = None
    taux_reussite: float | None = None
    roi_par_score: str | None = None
    roi_par_hippodrome: str | None = None
    roi_par_type_pari: str | None = None
    drawdown: float | None = None
    stabilite: float | None = None
    parametres: str | None = None
    commentaire: str | None = None
    source: str = "automatique"
    cree_le: datetime | None = None
