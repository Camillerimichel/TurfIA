"""Schémas du domaine Référentiels — cf. L007 §4.1, L030.1."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class HippodromeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    ville: str | None = None
    pays: str | None = None


class DisciplineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    libelle: str
    description: str | None = None
