"""Modèles des tables de référence — cf. L030.1, L015 §5."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Corde:
    libelle: str
    id: int | None = None


@dataclass
class Hippodrome:
    nom: str
    id: int | None = None
    ville: str | None = None
    pays: str | None = None
    corde_id: int | None = None
    altitude: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    cree_le: datetime | None = None


@dataclass
class Discipline:
    libelle: str
    id: int | None = None
    description: str | None = None


@dataclass
class Surface:
    libelle: str
    id: int | None = None
    description: str | None = None


@dataclass
class EtatPiste:
    libelle: str
    id: int | None = None
    indice: float | None = None


@dataclass
class TypeCourse:
    libelle: str
    id: int | None = None
    description: str | None = None


@dataclass
class Distance:
    distance: int
    id: int | None = None
    unite: str = "m"
