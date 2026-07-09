"""Schémas du module Administration — cf. L018 §10."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JournalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_evenement: datetime
    niveau: str
    composant: str | None = None
    correlation_id: str | None = None
    message: str
    exception: str | None = None


class TacheOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    categorie: str | None = None
    debut: datetime
    fin: datetime | None = None
    duree_ms: int | None = None
    statut: str
    commentaire: str | None = None


class ParametreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cle: str
    valeur: str
    type: str
    description: str | None = None
    date_modification: datetime


class ParametrePatchIn(BaseModel):
    valeur: str


class VersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version: str
    commit_git: str | None = None
    branche: str | None = None
    date_publication: datetime
    commentaire: str | None = None


class EtatSupervisionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    base_de_donnees_ok: bool
    latence_db_ms: float | None = None
    espace_disque_disponible_octets: int
    taches_en_echec_24h: int
    demarrage_processus: datetime
    uptime_secondes: float


class ErreurCourseOut(BaseModel):
    course_id: int
    message: str


class RapportAnalyseJourOut(BaseModel):
    nb_courses: int
    nb_erreurs: int
    erreurs: list[ErreurCourseOut]
