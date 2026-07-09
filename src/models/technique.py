"""Modèles des tables techniques d'administration — cf. L011 §10, L030.5,
L018 §10 (module Administration)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Journal:
    niveau: str
    message: str
    id: int | None = None
    date_evenement: datetime | None = None
    composant: str | None = None
    correlation_id: str | None = None
    exception: str | None = None


@dataclass(frozen=True)
class Tache:
    nom: str
    id: int | None = None
    categorie: str | None = None
    debut: datetime | None = None
    fin: datetime | None = None
    duree_ms: int | None = None
    statut: str = "en_cours"
    commentaire: str | None = None


@dataclass(frozen=True)
class Parametre:
    cle: str
    valeur: str
    id: int | None = None
    type: str = "String"
    description: str | None = None
    date_modification: datetime | None = None


@dataclass(frozen=True)
class Version:
    version: str
    id: int | None = None
    commit_git: str | None = None
    branche: str | None = None
    date_publication: datetime | None = None
    commentaire: str | None = None
