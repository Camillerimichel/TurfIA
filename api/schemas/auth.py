"""Schémas du domaine Authentification — cf. L021 §3."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class LoginIn(BaseModel):
    login: str
    mot_de_passe: str


class UtilisateurOut(BaseModel):
    id: int
    login: str
    nom: str | None = None
    role: str


class TokenOut(BaseModel):
    jeton: str
    expire_le: datetime
    utilisateur: UtilisateurOut
