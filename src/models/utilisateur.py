"""Modèles des tables techniques d'authentification — cf. L030.5, L021."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Role:
    nom: str
    id: int | None = None
    description: str | None = None


@dataclass
class Utilisateur:
    login: str
    mot_de_passe: str
    role_id: int
    id: int | None = None
    nom: str | None = None
    email: str | None = None
    actif: bool = True
    derniere_connexion: datetime | None = None


@dataclass
class Session:
    utilisateur_id: int
    jeton_hache: str
    expire_le: datetime
    id: int | None = None
    revoque_le: datetime | None = None
    derniere_utilisation: datetime | None = None
