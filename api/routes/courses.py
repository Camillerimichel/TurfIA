"""Routes du domaine Courses — cf. L007 §4.2, L030.2.

Chaque création vérifie l'existence de ses dépendances directes (réunion, course,
cheval, jockey, entraîneur) et répond 404 sinon, plutôt que de laisser remonter une
violation de contrainte SQL brute (cf. L016 §7, aucun détail technique interne
exposé).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies.auth import ECRITURE_DONNEES, LECTURE, exiger_roles
from api.dependencies.db import get_course_repository, get_referentiel_repository
from api.schemas.common import Enveloppe
from api.schemas.courses import (
    ChevalIn,
    ChevalOut,
    ChevalPatch,
    CoteIn,
    CoteOut,
    CourseIn,
    CourseOut,
    CoursePatch,
    EntraineurIn,
    EntraineurOut,
    EntraineurPatch,
    JockeyIn,
    JockeyOut,
    JockeyPatch,
    PartantIn,
    PartantOut,
    PartantPatch,
    ResultatIn,
    ResultatOut,
    ReunionIn,
    ReunionOut,
    ReunionPatch,
)
from src.models.course import Cheval, Cote, Course, Entraineur, Jockey, Partant, Resultat, Reunion
from src.models.utilisateur import Utilisateur
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


@router.patch("/reunions/{reunion_id}", response_model=Enveloppe[ReunionOut])
def update_reunion(
    reunion_id: int,
    payload: ReunionPatch,
    repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[ReunionOut]:
    reunion = repo.update_reunion(reunion_id, payload.model_dump(exclude_unset=True))
    if reunion is None:
        raise HTTPException(status_code=404, detail=f"Réunion {reunion_id} introuvable.")
    return Enveloppe(data=ReunionOut.model_validate(reunion))


@router.delete("/reunions/{reunion_id}", response_model=Enveloppe[dict])
def delete_reunion(
    reunion_id: int,
    repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[dict]:
    if not repo.delete_reunion(reunion_id):
        raise HTTPException(status_code=404, detail=f"Réunion {reunion_id} introuvable.")
    return Enveloppe(data={"supprime": True})


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


@router.patch("/courses/{course_id}", response_model=Enveloppe[CourseOut])
def update_course(
    course_id: int,
    payload: CoursePatch,
    repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[CourseOut]:
    course = repo.update_course(course_id, payload.model_dump(exclude_unset=True))
    if course is None:
        raise HTTPException(status_code=404, detail=f"Course {course_id} introuvable.")
    return Enveloppe(data=CourseOut.model_validate(course))


@router.delete("/courses/{course_id}", response_model=Enveloppe[dict])
def delete_course(
    course_id: int,
    repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[dict]:
    if not repo.delete_course(course_id):
        raise HTTPException(status_code=404, detail=f"Course {course_id} introuvable.")
    return Enveloppe(data={"supprime": True})


@router.post("/chevaux", response_model=Enveloppe[ChevalOut], status_code=201)
def create_cheval(payload: ChevalIn, repo: CourseRepository = Depends(get_course_repository)) -> Enveloppe[ChevalOut]:
    cheval = repo.create_cheval(Cheval(**payload.model_dump()))
    return Enveloppe(data=ChevalOut.model_validate(cheval))


@router.get("/chevaux/{cheval_id}", response_model=Enveloppe[ChevalOut])
def get_cheval(cheval_id: int, repo: CourseRepository = Depends(get_course_repository)) -> Enveloppe[ChevalOut]:
    cheval = repo.get_cheval(cheval_id)
    if cheval is None:
        raise HTTPException(status_code=404, detail=f"Cheval {cheval_id} introuvable.")
    return Enveloppe(data=ChevalOut.model_validate(cheval))


@router.patch("/chevaux/{cheval_id}", response_model=Enveloppe[ChevalOut])
def update_cheval(
    cheval_id: int,
    payload: ChevalPatch,
    repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[ChevalOut]:
    cheval = repo.update_cheval(cheval_id, payload.model_dump(exclude_unset=True))
    if cheval is None:
        raise HTTPException(status_code=404, detail=f"Cheval {cheval_id} introuvable.")
    return Enveloppe(data=ChevalOut.model_validate(cheval))


@router.delete("/chevaux/{cheval_id}", response_model=Enveloppe[dict])
def delete_cheval(
    cheval_id: int,
    repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[dict]:
    if not repo.delete_cheval(cheval_id):
        raise HTTPException(status_code=404, detail=f"Cheval {cheval_id} introuvable.")
    return Enveloppe(data={"supprime": True})


@router.post("/jockeys", response_model=Enveloppe[JockeyOut], status_code=201)
def create_jockey(payload: JockeyIn, repo: CourseRepository = Depends(get_course_repository)) -> Enveloppe[JockeyOut]:
    jockey = repo.create_jockey(Jockey(**payload.model_dump()))
    return Enveloppe(data=JockeyOut.model_validate(jockey))


@router.get("/jockeys/{jockey_id}", response_model=Enveloppe[JockeyOut])
def get_jockey(jockey_id: int, repo: CourseRepository = Depends(get_course_repository)) -> Enveloppe[JockeyOut]:
    jockey = repo.get_jockey(jockey_id)
    if jockey is None:
        raise HTTPException(status_code=404, detail=f"Jockey {jockey_id} introuvable.")
    return Enveloppe(data=JockeyOut.model_validate(jockey))


@router.patch("/jockeys/{jockey_id}", response_model=Enveloppe[JockeyOut])
def update_jockey(
    jockey_id: int,
    payload: JockeyPatch,
    repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[JockeyOut]:
    jockey = repo.update_jockey(jockey_id, payload.model_dump(exclude_unset=True))
    if jockey is None:
        raise HTTPException(status_code=404, detail=f"Jockey {jockey_id} introuvable.")
    return Enveloppe(data=JockeyOut.model_validate(jockey))


@router.delete("/jockeys/{jockey_id}", response_model=Enveloppe[dict])
def delete_jockey(
    jockey_id: int,
    repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[dict]:
    if not repo.delete_jockey(jockey_id):
        raise HTTPException(status_code=404, detail=f"Jockey {jockey_id} introuvable.")
    return Enveloppe(data={"supprime": True})


@router.post("/entraineurs", response_model=Enveloppe[EntraineurOut], status_code=201)
def create_entraineur(
    payload: EntraineurIn, repo: CourseRepository = Depends(get_course_repository)
) -> Enveloppe[EntraineurOut]:
    entraineur = repo.create_entraineur(Entraineur(**payload.model_dump()))
    return Enveloppe(data=EntraineurOut.model_validate(entraineur))


@router.get("/entraineurs/{entraineur_id}", response_model=Enveloppe[EntraineurOut])
def get_entraineur(
    entraineur_id: int, repo: CourseRepository = Depends(get_course_repository)
) -> Enveloppe[EntraineurOut]:
    entraineur = repo.get_entraineur(entraineur_id)
    if entraineur is None:
        raise HTTPException(status_code=404, detail=f"Entraîneur {entraineur_id} introuvable.")
    return Enveloppe(data=EntraineurOut.model_validate(entraineur))


@router.patch("/entraineurs/{entraineur_id}", response_model=Enveloppe[EntraineurOut])
def update_entraineur(
    entraineur_id: int,
    payload: EntraineurPatch,
    repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[EntraineurOut]:
    entraineur = repo.update_entraineur(entraineur_id, payload.model_dump(exclude_unset=True))
    if entraineur is None:
        raise HTTPException(status_code=404, detail=f"Entraîneur {entraineur_id} introuvable.")
    return Enveloppe(data=EntraineurOut.model_validate(entraineur))


@router.delete("/entraineurs/{entraineur_id}", response_model=Enveloppe[dict])
def delete_entraineur(
    entraineur_id: int,
    repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[dict]:
    if not repo.delete_entraineur(entraineur_id):
        raise HTTPException(status_code=404, detail=f"Entraîneur {entraineur_id} introuvable.")
    return Enveloppe(data={"supprime": True})


@router.post("/courses/{course_id}/partants", response_model=Enveloppe[PartantOut], status_code=201)
def create_partant(
    course_id: int, payload: PartantIn, repo: CourseRepository = Depends(get_course_repository)
) -> Enveloppe[PartantOut]:
    if repo.get_course(course_id) is None:
        raise HTTPException(status_code=404, detail=f"Course {course_id} introuvable.")
    if repo.get_cheval(payload.cheval_id) is None:
        raise HTTPException(status_code=404, detail=f"Cheval {payload.cheval_id} introuvable.")
    if payload.jockey_id is not None and repo.get_jockey(payload.jockey_id) is None:
        raise HTTPException(status_code=404, detail=f"Jockey {payload.jockey_id} introuvable.")
    if payload.entraineur_id is not None and repo.get_entraineur(payload.entraineur_id) is None:
        raise HTTPException(status_code=404, detail=f"Entraîneur {payload.entraineur_id} introuvable.")
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


@router.get("/partants/{partant_id}", response_model=Enveloppe[PartantOut])
def get_partant(partant_id: int, repo: CourseRepository = Depends(get_course_repository)) -> Enveloppe[PartantOut]:
    partant = repo.get_partant(partant_id)
    if partant is None:
        raise HTTPException(status_code=404, detail=f"Partant {partant_id} introuvable.")
    return Enveloppe(data=PartantOut.model_validate(partant))


@router.patch("/partants/{partant_id}", response_model=Enveloppe[PartantOut])
def update_partant(
    partant_id: int,
    payload: PartantPatch,
    repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[PartantOut]:
    champs = payload.model_dump(exclude_unset=True)
    if "jockey_id" in champs and champs["jockey_id"] is not None and repo.get_jockey(champs["jockey_id"]) is None:
        raise HTTPException(status_code=404, detail=f"Jockey {champs['jockey_id']} introuvable.")
    if (
        "entraineur_id" in champs
        and champs["entraineur_id"] is not None
        and repo.get_entraineur(champs["entraineur_id"]) is None
    ):
        raise HTTPException(status_code=404, detail=f"Entraîneur {champs['entraineur_id']} introuvable.")
    partant = repo.update_partant(partant_id, champs)
    if partant is None:
        raise HTTPException(status_code=404, detail=f"Partant {partant_id} introuvable.")
    return Enveloppe(data=PartantOut.model_validate(partant))


@router.delete("/partants/{partant_id}", response_model=Enveloppe[dict])
def delete_partant(
    partant_id: int,
    repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[dict]:
    if not repo.delete_partant(partant_id):
        raise HTTPException(status_code=404, detail=f"Partant {partant_id} introuvable.")
    return Enveloppe(data={"supprime": True})


@router.post("/courses/{course_id}/resultats", response_model=Enveloppe[ResultatOut], status_code=201)
def create_resultat(
    course_id: int,
    payload: ResultatIn,
    repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[ResultatOut]:
    """Toujours une création (get-or-create sur `(course_id, classement)`) : un
    résultat officiel est figé une fois validé, jamais modifié ni supprimé (cf.
    L011 §15, L009 §5.1) — aucun PATCH/DELETE n'est exposé sur cette ressource."""
    if repo.get_course(course_id) is None:
        raise HTTPException(status_code=404, detail=f"Course {course_id} introuvable.")
    if repo.get_partant(payload.partant_id) is None:
        raise HTTPException(status_code=404, detail=f"Partant {payload.partant_id} introuvable.")
    resultat = repo.get_or_create_resultat(Resultat(course_id=course_id, **payload.model_dump()))
    return Enveloppe(data=ResultatOut.model_validate(resultat))


@router.get("/courses/{course_id}/resultats", response_model=Enveloppe[list[ResultatOut]])
def list_resultats(
    course_id: int,
    repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*LECTURE)),
) -> Enveloppe[list[ResultatOut]]:
    if repo.get_course(course_id) is None:
        raise HTTPException(status_code=404, detail=f"Course {course_id} introuvable.")
    resultats = repo.list_resultats_by_course(course_id)
    return Enveloppe(data=[ResultatOut.model_validate(r) for r in resultats])


@router.post("/partants/{partant_id}/cotes", response_model=Enveloppe[CoteOut], status_code=201)
def create_cote(
    partant_id: int,
    payload: CoteIn,
    repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[CoteOut]:
    """Toujours une création : une cote n'est jamais remplacée mais historisée
    (cf. L011 §15) — aucun PATCH/DELETE n'est exposé sur cette ressource."""
    if repo.get_partant(partant_id) is None:
        raise HTTPException(status_code=404, detail=f"Partant {partant_id} introuvable.")
    cote = repo.create_cote(Cote(partant_id=partant_id, **payload.model_dump()))
    return Enveloppe(data=CoteOut.model_validate(cote))


@router.get("/partants/{partant_id}/cotes", response_model=Enveloppe[list[CoteOut]])
def list_cotes(
    partant_id: int,
    repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*LECTURE)),
) -> Enveloppe[list[CoteOut]]:
    if repo.get_partant(partant_id) is None:
        raise HTTPException(status_code=404, detail=f"Partant {partant_id} introuvable.")
    cotes = repo.list_cotes_by_partant(partant_id)
    return Enveloppe(data=[CoteOut.model_validate(c) for c in cotes])
