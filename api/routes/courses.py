"""Routes du domaine Courses — cf. L007 §4.2, L030.2.

Chaque création vérifie l'existence de ses dépendances directes (réunion, course,
cheval) et répond 404 sinon, plutôt que de laisser remonter une violation de
contrainte SQL brute (cf. L016 §7, aucun détail technique interne exposé).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies.db import get_course_repository, get_referentiel_repository
from api.schemas.common import Enveloppe
from api.schemas.courses import ChevalIn, ChevalOut, CourseIn, CourseOut, PartantIn, PartantOut, ReunionIn, ReunionOut
from src.models.course import Cheval, Course, Partant, Reunion
from src.repositories.course_repository import CourseRepository
from src.repositories.referentiel_repository import ReferentielRepository

router = APIRouter(tags=["Courses"])


@router.post("/reunions", response_model=Enveloppe[ReunionOut], status_code=201)
def create_reunion(
    payload: ReunionIn,
    repo: CourseRepository = Depends(get_course_repository),
    referentiel_repo: ReferentielRepository = Depends(get_referentiel_repository),
) -> Enveloppe[ReunionOut]:
    if referentiel_repo.get_hippodrome(payload.hippodrome_id) is None:
        raise HTTPException(status_code=404, detail=f"Hippodrome {payload.hippodrome_id} introuvable.")
    reunion = repo.create_reunion(Reunion(**payload.model_dump()))
    return Enveloppe(data=ReunionOut.model_validate(reunion))


@router.get("/reunions/{reunion_id}", response_model=Enveloppe[ReunionOut])
def get_reunion(reunion_id: int, repo: CourseRepository = Depends(get_course_repository)) -> Enveloppe[ReunionOut]:
    reunion = repo.get_reunion(reunion_id)
    if reunion is None:
        raise HTTPException(status_code=404, detail=f"Réunion {reunion_id} introuvable.")
    return Enveloppe(data=ReunionOut.model_validate(reunion))


@router.post("/reunions/{reunion_id}/courses", response_model=Enveloppe[CourseOut], status_code=201)
def create_course(
    reunion_id: int, payload: CourseIn, repo: CourseRepository = Depends(get_course_repository)
) -> Enveloppe[CourseOut]:
    if repo.get_reunion(reunion_id) is None:
        raise HTTPException(status_code=404, detail=f"Réunion {reunion_id} introuvable.")
    course = repo.create_course(Course(reunion_id=reunion_id, **payload.model_dump()))
    return Enveloppe(data=CourseOut.model_validate(course))


@router.get("/reunions/{reunion_id}/courses", response_model=Enveloppe[list[CourseOut]])
def list_courses(
    reunion_id: int, repo: CourseRepository = Depends(get_course_repository)
) -> Enveloppe[list[CourseOut]]:
    if repo.get_reunion(reunion_id) is None:
        raise HTTPException(status_code=404, detail=f"Réunion {reunion_id} introuvable.")
    courses = repo.list_courses_by_reunion(reunion_id)
    return Enveloppe(data=[CourseOut.model_validate(c) for c in courses])


@router.get("/courses/{course_id}", response_model=Enveloppe[CourseOut])
def get_course(course_id: int, repo: CourseRepository = Depends(get_course_repository)) -> Enveloppe[CourseOut]:
    course = repo.get_course(course_id)
    if course is None:
        raise HTTPException(status_code=404, detail=f"Course {course_id} introuvable.")
    return Enveloppe(data=CourseOut.model_validate(course))


@router.post("/chevaux", response_model=Enveloppe[ChevalOut], status_code=201)
def create_cheval(payload: ChevalIn, repo: CourseRepository = Depends(get_course_repository)) -> Enveloppe[ChevalOut]:
    cheval = repo.create_cheval(Cheval(**payload.model_dump()))
    return Enveloppe(data=ChevalOut.model_validate(cheval))


@router.post("/courses/{course_id}/partants", response_model=Enveloppe[PartantOut], status_code=201)
def create_partant(
    course_id: int, payload: PartantIn, repo: CourseRepository = Depends(get_course_repository)
) -> Enveloppe[PartantOut]:
    if repo.get_course(course_id) is None:
        raise HTTPException(status_code=404, detail=f"Course {course_id} introuvable.")
    if repo.get_cheval(payload.cheval_id) is None:
        raise HTTPException(status_code=404, detail=f"Cheval {payload.cheval_id} introuvable.")
    partant = repo.create_partant(Partant(course_id=course_id, **payload.model_dump()))
    return Enveloppe(data=PartantOut.model_validate(partant))


@router.get("/courses/{course_id}/partants", response_model=Enveloppe[list[PartantOut]])
def list_partants(
    course_id: int, repo: CourseRepository = Depends(get_course_repository)
) -> Enveloppe[list[PartantOut]]:
    if repo.get_course(course_id) is None:
        raise HTTPException(status_code=404, detail=f"Course {course_id} introuvable.")
    partants = repo.list_partants_by_course(course_id)
    return Enveloppe(data=[PartantOut.model_validate(p) for p in partants])
