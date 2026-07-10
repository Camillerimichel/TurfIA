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
    hippodrome_nom: str | None = None
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
    """Les champs `*_nom`/`*_prenom`/`derniere_cote*` ne sont peuplés que par
    `GET /courses/{id}/partants` (jointure, cf. `PartantDetail`) ; `GET
    /partants/{id}` (lecture isolée, sur `Partant` brut) les laisse à `None`."""

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
    cheval_nom: str | None = None
    jockey_nom: str | None = None
    jockey_prenom: str | None = None
    entraineur_nom: str | None = None
    entraineur_prenom: str | None = None
    derniere_cote: float | None = None
    derniere_cote_operateur: str | None = None


class ResultatIn(BaseModel):
    partant_id: int
    classement: int | None = None
    temps: str | None = None
    ecart: str | None = None
    disqualification: bool = False
    non_partant: bool = False


class ResultatOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    partant_id: int
    classement: int | None = None
    temps: str | None = None
    ecart: str | None = None
    disqualification: bool
    non_partant: bool


class CoteIn(BaseModel):
    operateur: str
    cote: float
    evolution: float | None = None


class CoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    partant_id: int
    operateur: str
    cote: float
    evolution: float | None = None
    date_maj: datetime


# Schémas PATCH — correction partielle des ressources mutables (cf. plan
# "Résultats/cotes en écriture, PATCH/DELETE, authentification réelle"). Tous les
# champs sont optionnels ; seuls ceux effectivement fournis sont modifiés
# (`exclude_unset`, cf. api/routes/courses.py). Jamais de PATCH pour résultat/cote
# (historisés, cf. L011 §15).


class ReunionPatch(BaseModel):
    statut: str | None = None
    heure_debut: datetime | None = None
    heure_fin: datetime | None = None


class CoursePatch(BaseModel):
    nom: str | None = None
    heure_depart: datetime | None = None
    discipline_id: int | None = None
    type_course_id: int | None = None
    distance_id: int | None = None
    surface_id: int | None = None
    etat_piste_id: int | None = None
    allocation: float | None = None
    nb_partants: int | None = None
    quinte: bool | None = None


class PartantPatch(BaseModel):
    jockey_id: int | None = None
    entraineur_id: int | None = None
    corde: int | None = None
    poids: float | None = None
    valeur: float | None = None
    age: int | None = None
    ferrure: str | None = None
    musique: str | None = None
    non_partant: bool | None = None


class ChevalPatch(BaseModel):
    nom: str | None = None
    sexe: str | None = Field(default=None, pattern="^[MFH]$")
    date_naissance: date | None = None
    pere: str | None = None
    mere: str | None = None
    musique: str | None = None
    actif: bool | None = None


class JockeyPatch(BaseModel):
    nom: str | None = None
    prenom: str | None = None
    licence: str | None = None
    actif: bool | None = None


class EntraineurPatch(BaseModel):
    nom: str | None = None
    prenom: str | None = None
    actif: bool | None = None
