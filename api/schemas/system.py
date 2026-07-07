"""Schémas du domaine Administration/Système — cf. L007 §4.5."""

from __future__ import annotations

from pydantic import BaseModel


class SanteReponse(BaseModel):
    statut: str = "ok"


class VersionReponse(BaseModel):
    version: str
