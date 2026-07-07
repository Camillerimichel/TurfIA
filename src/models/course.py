"""Modèles des tables métier — cf. L030.2, L015 §5."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class Reunion:
    date: date
    hippodrome_id: int
    numero: int
    id: int | None = None
    heure_debut: datetime | None = None
    heure_fin: datetime | None = None
    statut: str = "Prévue"


@dataclass
class Course:
    reunion_id: int
    numero: int
    nom: str
    id: int | None = None
    heure_depart: datetime | None = None
    discipline_id: int | None = None
    type_course_id: int | None = None
    distance_id: int | None = None
    surface_id: int | None = None
    etat_piste_id: int | None = None
    allocation: float | None = None
    nb_partants: int | None = None
    quinte: bool = False


@dataclass
class Cheval:
    nom: str
    id: int | None = None
    sexe: str | None = None
    date_naissance: date | None = None
    pere: str | None = None
    mere: str | None = None
    gains: float = 0.0
    musique: str | None = None
    actif: bool = True


@dataclass
class Jockey:
    nom: str
    id: int | None = None
    prenom: str | None = None
    licence: str | None = None
    actif: bool = True


@dataclass
class Entraineur:
    nom: str
    id: int | None = None
    prenom: str | None = None
    actif: bool = True


@dataclass
class Partant:
    course_id: int
    cheval_id: int
    numero: int
    id: int | None = None
    jockey_id: int | None = None
    entraineur_id: int | None = None
    corde: int | None = None
    poids: float | None = None
    valeur: float | None = None
    age: int | None = None
    ferrure: str | None = None
    musique: str | None = None
    non_partant: bool = False


@dataclass
class Cote:
    partant_id: int
    operateur: str
    cote: float
    id: int | None = None
    evolution: float | None = None
    date_maj: datetime | None = None


@dataclass
class Resultat:
    course_id: int
    partant_id: int
    id: int | None = None
    classement: int | None = None
    temps: str | None = None
    ecart: str | None = None
    disqualification: bool = False
    non_partant: bool = False
