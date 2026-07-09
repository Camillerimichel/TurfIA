"""Modèles des tables statistiques — cf. L030.4, L015 §5.

Toutes historisées (cf. L030.4 §10) : un recalcul insère toujours une nouvelle
ligne, jamais une mise à jour en place — aucun champ `modifie_le`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class StatistiqueGlobale:
    id: int | None = None
    date_calcul: datetime | None = None
    nb_courses: int = 0
    nb_jouees: int = 0
    nb_ignorees: int = 0
    mises: float = 0.0
    gains: float = 0.0
    profit: float | None = None
    roi: float | None = None
    taux_reussite: float | None = None


@dataclass(frozen=True)
class StatistiqueScore:
    score_min: float
    score_max: float
    id: int | None = None
    nb_courses: int = 0
    nb_gagnantes: int = 0
    roi: float | None = None
    taux_reussite: float | None = None


@dataclass(frozen=True)
class StatistiqueHippodrome:
    hippodrome_id: int
    id: int | None = None
    nb_courses: int = 0
    mises: float = 0.0
    gains: float = 0.0
    profit: float | None = None
    roi: float | None = None


@dataclass(frozen=True)
class StatistiqueDiscipline:
    discipline_id: int
    id: int | None = None
    nb_courses: int = 0
    mises: float = 0.0
    gains: float = 0.0
    profit: float | None = None
    roi: float | None = None


@dataclass(frozen=True)
class StatistiquePari:
    type_pari: str
    id: int | None = None
    nb_paris: int = 0
    mises: float = 0.0
    gains: float = 0.0
    profit: float | None = None
    roi: float | None = None
    taux_reussite: float | None = None


@dataclass(frozen=True)
class StatistiqueModele:
    version_modele: str
    id: int | None = None
    date_debut: date | None = None
    date_fin: date | None = None
    nb_courses: int = 0
    roi: float | None = None
    taux_reussite: float | None = None
    roi_par_score: str | None = None
    roi_par_hippodrome: str | None = None
    roi_par_type_pari: str | None = None
    drawdown: float | None = None
    stabilite: float | None = None
    parametres: str | None = None
    commentaire: str | None = None
