"""Modèles du module Historique (L018 §8) — recherche transversale en lecture
seule sur analyses/paris/ROI, jamais persistés (pas de table dédiée)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class HistoriqueFiltres:
    date_debut: date | None = None
    date_fin: date | None = None
    hippodrome_id: int | None = None
    type_pari: str | None = None
    decisions: list[str] | None = None
    limite: int = 200


@dataclass(frozen=True)
class HistoriqueLigne:
    """Une ligne = un pari (avec l'analyse et le contrôle ROI qui s'y rattachent),
    pour la dernière version d'analyse connue de chaque course (une course
    réanalysée à chaque passage de l'automatisation horaire, cf. L033, ne doit
    apparaître qu'une fois ici — l'historique des versions reste consultable
    via `course.html?id=`). Une analyse sans pari (décision Ne pas jouer)
    apparaît une fois avec les colonnes de pari à `None` (LEFT JOIN)."""

    date: date
    hippodrome_id: int
    hippodrome_nom: str
    course_id: int
    course_numero: int
    course_nom: str
    analyse_id: int
    version: int
    date_calcul: datetime | None
    decision: str | None
    score_confiance: float | None
    risque: float | None
    budget: float
    pari_id: int | None = None
    type_pari: str | None = None
    mise: float | None = None
    gain_estime: float | None = None
    roi_estime: float | None = None
    roi_reel: float | None = None
    profit_reel: float | None = None
    valide: bool | None = None
