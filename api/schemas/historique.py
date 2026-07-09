"""Schéma du module Historique — cf. L018 §8."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict


class HistoriqueLigneOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: date
    hippodrome_id: int
    hippodrome_nom: str
    course_id: int
    course_numero: int
    course_nom: str
    analyse_id: int
    version: int
    decision: str | None = None
    score_confiance: float | None = None
    risque: float | None = None
    budget: float
    pari_id: int | None = None
    type_pari: str | None = None
    mise: float | None = None
    gain_estime: float | None = None
    roi_estime: float | None = None
    roi_reel: float | None = None
    profit_reel: float | None = None
    valide: bool | None = None
