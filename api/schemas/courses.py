"""Schémas du domaine Courses — cf. L007 §4.2, L030.2."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ReunionIn(BaseModel):
    date: date
    hippodrome_id: int
    numero: int = Field(gt=0)
    heure_debut: datetime | None = None
    heure_fin: datetime | None = None
    statut: str = "Prévue"


class ReunionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date
    hippodrome_id: int
    numero: int
    heure_debut: datetime | None = None
    heure_fin: datetime | None = None
    statut: str


class CourseIn(BaseModel):
    numero: int = Field(gt=0)
    nom: str
    heure_depart: datetime | None = None
    discipline_id: int | None = None
    type_course_id: int | None = None
    distance_id: int | None = None
    surface_id: int | None = None
    etat_piste_id: int | None = None
    allocation: float | None = None
    nb_partants: int | None = None
    quinte: bool = False


class CourseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reunion_id: int
    numero: int
    nom: str
    heure_depart: datetime | None = None
    discipline_id: int | None = None
    type_course_id: int | None = None
    distance_id: int | None = None
    surface_id: int | None = None
    etat_piste_id: int | None = None
    allocation: float | None = None
    nb_partants: int | None = None
    quinte: bool


class ChevalIn(BaseModel):
    nom: str
    sexe: str | None = Field(default=None, pattern="^[MFH]$")
    date_naissance: date | None = None
    pere: str | None = None
    mere: str | None = None
    musique: str | None = None


class ChevalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    sexe: str | None = None
    date_naissance: date | None = None
    pere: str | None = None
    mere: str | None = None
    gains: float
    musique: str | None = None
    actif: bool


class JockeyIn(BaseModel):
    nom: str
    prenom: str | None = None
    licence: str | None = None


class JockeyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    prenom: str | None = None
    licence: str | None = None
    actif: bool


class EntraineurIn(BaseModel):
    nom: str
    prenom: str | None = None


class EntraineurOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    prenom: str | None = None
    actif: bool


class PartantIn(BaseModel):
    cheval_id: int
    numero: int = Field(gt=0)
    jockey_id: int | None = None
    entraineur_id: int | None = None
    corde: int | None = None
    poids: float | None = None
    valeur: float | None = None
    age: int | None = None
    ferrure: str | None = None
    musique: str | None = None


class PartantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    cheval_id: int
    jockey_id: int | None = None
    entraineur_id: int | None = None
    numero: int
    corde: int | None = None
    poids: float | None = None
    valeur: float | None = None
    age: int | None = None
    ferrure: str | None = None
    musique: str | None = None
    non_partant: bool
