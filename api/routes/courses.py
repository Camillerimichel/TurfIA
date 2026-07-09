"""Routes du domaine Courses — cf. L007 §4.2, L030.2.

Chaque création vérifie l'existence de ses dépendances directes (réunion, course,
cheval, jockey, entraîneur) et répond 404 sinon, plutôt que de laisser remonter une
violation de contrainte SQL brute (cf. L016 §7, aucun détail technique interne
exposé).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies.auth import ECRITURE_DONNEES, LECTURE, exiger_roles
from api.dependencies.db import get_audit_repository, get_course_repository, get_referentiel_repository
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
from src.core.audit import serialiser_etat
from src.models.course import Cheval, Cote, Course, Entraineur, Jockey, Partant, Resultat, Reunion
from src.models.utilisateur import Utilisateur
from src.repositories.audit_repository import AuditRepository
from src.repositories.course_repository import CourseRepository
from src.repositories.referentiel_repository import ReferentielRepository

router = APIRouter(tags=["Courses"])


@router.post("/reunions", response_model=Enveloppe[ReunionOut], status_code=201)
def create_reunion(
    payload: ReunionIn,
    repo: CourseRepository = Depends(get_course_repository),
    referentiel_repo: ReferentielRepository = Depends(get_referentiel_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[ReunionOut]:
    if referentiel_repo.get_hippodrome(payload.hippodrome_id) is None:
        raise HTTPException(status_code=404, detail=f"Hippodrome {payload.hippodrome_id} introuvable.")
    reunion = repo.create_reunion(Reunion(**payload.model_dump()))
    audit_repo.enregistrer(utilisateur.id, "creation_reunion", objet=str(reunion.id), nouvel_etat=serialiser_etat(reunion))
    return Enveloppe(data=ReunionOut.model_validate(reunion))


@router.get("/reunions/{reunion_id}", response_model=Enveloppe[ReunionOut])
def get_reunion(
    reunion_id: int,
    repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*LECTURE)),
) -> Enveloppe[ReunionOut]:
    reunion = repo.get_reunion(reunion_id)
    if reunion is None:
        raise HTTPException(status_code=404, detail=f"Réunion {reunion_id} introuvable.")
    return Enveloppe(data=ReunionOut.model_validate(reunion))


@router.patch("/reunions/{reunion_id}", response_model=Enveloppe[ReunionOut])
def update_reunion(
    reunion_id: int,
    payload: ReunionPatch,
    repo: CourseRepository = Depends(get_course_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[ReunionOut]:
    ancien = repo.get_reunion(reunion_id)
    if ancien is None:
        raise HTTPException(status_code=404, detail=f"Réunion {reunion_id} introuvable.")
    reunion = repo.update_reunion(reunion_id, payload.model_dump(exclude_unset=True))
    audit_repo.enregistrer(
        utilisateur.id, "modification_reunion", objet=str(reunion_id),
        ancien_etat=serialiser_etat(ancien), nouvel_etat=serialiser_etat(reunion),
    )
    return Enveloppe(data=ReunionOut.model_validate(reunion))


@router.delete("/reunions/{reunion_id}", response_model=Enveloppe[dict])
def delete_reunion(
    reunion_id: int,
    repo: CourseRepository = Depends(get_course_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[dict]:
    ancien = repo.get_reunion(reunion_id)
    if ancien is None:
        raise HTTPException(status_code=404, detail=f"Réunion {reunion_id} introuvable.")
    repo.delete_reunion(reunion_id)
    audit_repo.enregistrer(utilisateur.id, "suppression_reunion", objet=str(reunion_id), ancien_etat=serialiser_etat(ancien))
    return Enveloppe(data={"supprime": True})


def _valider_referentiels_course(champs: dict, referentiel_repo: ReferentielRepository) -> None:
    """Vérifie l'existence des référentiels optionnels d'une course avant
    écriture (404 ciblé plutôt qu'une violation de contrainte FK brute en 500,
    même principe déjà appliqué à `jockey_id`/`entraineur_id` sur un partant)."""
    verifications = {
        "discipline_id": ("Discipline", referentiel_repo.get_discipline),
        "type_course_id": ("Type de course", referentiel_repo.get_type_course),
        "distance_id": ("Distance", referentiel_repo.get_distance),
        "surface_id": ("Surface", referentiel_repo.get_surface),
        "etat_piste_id": ("État de piste", referentiel_repo.get_etat_piste),
    }
    for champ, (libelle, getter) in verifications.items():
        valeur = champs.get(champ)
        if valeur is not None and getter(valeur) is None:
            raise HTTPException(status_code=404, detail=f"{libelle} {valeur} introuvable.")


@router.post("/reunions/{reunion_id}/courses", response_model=Enveloppe[CourseOut], status_code=201)
def create_course(
    reunion_id: int,
    payload: CourseIn,
    repo: CourseRepository = Depends(get_course_repository),
    referentiel_repo: ReferentielRepository = Depends(get_referentiel_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[CourseOut]:
    if repo.get_reunion(reunion_id) is None:
        raise HTTPException(status_code=404, detail=f"Réunion {reunion_id} introuvable.")
    champs = payload.model_dump()
    _valider_referentiels_course(champs, referentiel_repo)
    course = repo.create_course(Course(reunion_id=reunion_id, **champs))
    audit_repo.enregistrer(utilisateur.id, "creation_course", objet=str(course.id), nouvel_etat=serialiser_etat(course))
    return Enveloppe(data=CourseOut.model_validate(course))


@router.get("/reunions/{reunion_id}/courses", response_model=Enveloppe[list[CourseOut]])
def list_courses(
    reunion_id: int,
    repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*LECTURE)),
) -> Enveloppe[list[CourseOut]]:
    if repo.get_reunion(reunion_id) is None:
        raise HTTPException(status_code=404, detail=f"Réunion {reunion_id} introuvable.")
    courses = repo.list_courses_by_reunion(reunion_id)
    return Enveloppe(data=[CourseOut.model_validate(c) for c in courses])


@router.get("/courses/{course_id}", response_model=Enveloppe[CourseOut])
def get_course(
    course_id: int,
    repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*LECTURE)),
) -> Enveloppe[CourseOut]:
    course = repo.get_course(course_id)
    if course is None:
        raise HTTPException(status_code=404, detail=f"Course {course_id} introuvable.")
    return Enveloppe(data=CourseOut.model_validate(course))


@router.patch("/courses/{course_id}", response_model=Enveloppe[CourseOut])
def update_course(
    course_id: int,
    payload: CoursePatch,
    repo: CourseRepository = Depends(get_course_repository),
    referentiel_repo: ReferentielRepository = Depends(get_referentiel_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[CourseOut]:
    ancien = repo.get_course(course_id)
    if ancien is None:
        raise HTTPException(status_code=404, detail=f"Course {course_id} introuvable.")
    champs = payload.model_dump(exclude_unset=True)
    _valider_referentiels_course(champs, referentiel_repo)
    course = repo.update_course(course_id, champs)
    audit_repo.enregistrer(
        utilisateur.id, "modification_course", objet=str(course_id),
        ancien_etat=serialiser_etat(ancien), nouvel_etat=serialiser_etat(course),
    )
    return Enveloppe(data=CourseOut.model_validate(course))


@router.delete("/courses/{course_id}", response_model=Enveloppe[dict])
def delete_course(
    course_id: int,
    repo: CourseRepository = Depends(get_course_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[dict]:
    ancien = repo.get_course(course_id)
    if ancien is None:
        raise HTTPException(status_code=404, detail=f"Course {course_id} introuvable.")
    repo.delete_course(course_id)
    audit_repo.enregistrer(utilisateur.id, "suppression_course", objet=str(course_id), ancien_etat=serialiser_etat(ancien))
    return Enveloppe(data={"supprime": True})


@router.post("/chevaux", response_model=Enveloppe[ChevalOut], status_code=201)
def create_cheval(
    payload: ChevalIn,
    repo: CourseRepository = Depends(get_course_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[ChevalOut]:
    cheval = repo.create_cheval(Cheval(**payload.model_dump()))
    audit_repo.enregistrer(utilisateur.id, "creation_cheval", objet=str(cheval.id), nouvel_etat=serialiser_etat(cheval))
    return Enveloppe(data=ChevalOut.model_validate(cheval))


@router.get("/chevaux/{cheval_id}", response_model=Enveloppe[ChevalOut])
def get_cheval(
    cheval_id: int,
    repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*LECTURE)),
) -> Enveloppe[ChevalOut]:
    cheval = repo.get_cheval(cheval_id)
    if cheval is None:
        raise HTTPException(status_code=404, detail=f"Cheval {cheval_id} introuvable.")
    return Enveloppe(data=ChevalOut.model_validate(cheval))


@router.patch("/chevaux/{cheval_id}", response_model=Enveloppe[ChevalOut])
def update_cheval(
    cheval_id: int,
    payload: ChevalPatch,
    repo: CourseRepository = Depends(get_course_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[ChevalOut]:
    ancien = repo.get_cheval(cheval_id)
    if ancien is None:
        raise HTTPException(status_code=404, detail=f"Cheval {cheval_id} introuvable.")
    cheval = repo.update_cheval(cheval_id, payload.model_dump(exclude_unset=True))
    audit_repo.enregistrer(
        utilisateur.id, "modification_cheval", objet=str(cheval_id),
        ancien_etat=serialiser_etat(ancien), nouvel_etat=serialiser_etat(cheval),
    )
    return Enveloppe(data=ChevalOut.model_validate(cheval))


@router.delete("/chevaux/{cheval_id}", response_model=Enveloppe[dict])
def delete_cheval(
    cheval_id: int,
    repo: CourseRepository = Depends(get_course_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[dict]:
    ancien = repo.get_cheval(cheval_id)
    if ancien is None:
        raise HTTPException(status_code=404, detail=f"Cheval {cheval_id} introuvable.")
    repo.delete_cheval(cheval_id)
    audit_repo.enregistrer(utilisateur.id, "suppression_cheval", objet=str(cheval_id), ancien_etat=serialiser_etat(ancien))
    return Enveloppe(data={"supprime": True})


@router.post("/jockeys", response_model=Enveloppe[JockeyOut], status_code=201)
def create_jockey(
    payload: JockeyIn,
    repo: CourseRepository = Depends(get_course_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[JockeyOut]:
    jockey = repo.create_jockey(Jockey(**payload.model_dump()))
    audit_repo.enregistrer(utilisateur.id, "creation_jockey", objet=str(jockey.id), nouvel_etat=serialiser_etat(jockey))
    return Enveloppe(data=JockeyOut.model_validate(jockey))


@router.get("/jockeys/{jockey_id}", response_model=Enveloppe[JockeyOut])
def get_jockey(
    jockey_id: int,
    repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*LECTURE)),
) -> Enveloppe[JockeyOut]:
    jockey = repo.get_jockey(jockey_id)
    if jockey is None:
        raise HTTPException(status_code=404, detail=f"Jockey {jockey_id} introuvable.")
    return Enveloppe(data=JockeyOut.model_validate(jockey))


@router.patch("/jockeys/{jockey_id}", response_model=Enveloppe[JockeyOut])
def update_jockey(
    jockey_id: int,
    payload: JockeyPatch,
    repo: CourseRepository = Depends(get_course_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[JockeyOut]:
    ancien = repo.get_jockey(jockey_id)
    if ancien is None:
        raise HTTPException(status_code=404, detail=f"Jockey {jockey_id} introuvable.")
    jockey = repo.update_jockey(jockey_id, payload.model_dump(exclude_unset=True))
    audit_repo.enregistrer(
        utilisateur.id, "modification_jockey", objet=str(jockey_id),
        ancien_etat=serialiser_etat(ancien), nouvel_etat=serialiser_etat(jockey),
    )
    return Enveloppe(data=JockeyOut.model_validate(jockey))


@router.delete("/jockeys/{jockey_id}", response_model=Enveloppe[dict])
def delete_jockey(
    jockey_id: int,
    repo: CourseRepository = Depends(get_course_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[dict]:
    ancien = repo.get_jockey(jockey_id)
    if ancien is None:
        raise HTTPException(status_code=404, detail=f"Jockey {jockey_id} introuvable.")
    repo.delete_jockey(jockey_id)
    audit_repo.enregistrer(utilisateur.id, "suppression_jockey", objet=str(jockey_id), ancien_etat=serialiser_etat(ancien))
    return Enveloppe(data={"supprime": True})


@router.post("/entraineurs", response_model=Enveloppe[EntraineurOut], status_code=201)
def create_entraineur(
    payload: EntraineurIn,
    repo: CourseRepository = Depends(get_course_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[EntraineurOut]:
    entraineur = repo.create_entraineur(Entraineur(**payload.model_dump()))
    audit_repo.enregistrer(
        utilisateur.id, "creation_entraineur", objet=str(entraineur.id), nouvel_etat=serialiser_etat(entraineur)
    )
    return Enveloppe(data=EntraineurOut.model_validate(entraineur))


@router.get("/entraineurs/{entraineur_id}", response_model=Enveloppe[EntraineurOut])
def get_entraineur(
    entraineur_id: int,
    repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*LECTURE)),
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
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[EntraineurOut]:
    ancien = repo.get_entraineur(entraineur_id)
    if ancien is None:
        raise HTTPException(status_code=404, detail=f"Entraîneur {entraineur_id} introuvable.")
    entraineur = repo.update_entraineur(entraineur_id, payload.model_dump(exclude_unset=True))
    audit_repo.enregistrer(
        utilisateur.id, "modification_entraineur", objet=str(entraineur_id),
        ancien_etat=serialiser_etat(ancien), nouvel_etat=serialiser_etat(entraineur),
    )
    return Enveloppe(data=EntraineurOut.model_validate(entraineur))


@router.delete("/entraineurs/{entraineur_id}", response_model=Enveloppe[dict])
def delete_entraineur(
    entraineur_id: int,
    repo: CourseRepository = Depends(get_course_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[dict]:
    ancien = repo.get_entraineur(entraineur_id)
    if ancien is None:
        raise HTTPException(status_code=404, detail=f"Entraîneur {entraineur_id} introuvable.")
    repo.delete_entraineur(entraineur_id)
    audit_repo.enregistrer(
        utilisateur.id, "suppression_entraineur", objet=str(entraineur_id), ancien_etat=serialiser_etat(ancien)
    )
    return Enveloppe(data={"supprime": True})


@router.post("/courses/{course_id}/partants", response_model=Enveloppe[PartantOut], status_code=201)
def create_partant(
    course_id: int,
    payload: PartantIn,
    repo: CourseRepository = Depends(get_course_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
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
    audit_repo.enregistrer(utilisateur.id, "creation_partant", objet=str(partant.id), nouvel_etat=serialiser_etat(partant))
    return Enveloppe(data=PartantOut.model_validate(partant))


@router.get("/courses/{course_id}/partants", response_model=Enveloppe[list[PartantOut]])
def list_partants(
    course_id: int,
    repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*LECTURE)),
) -> Enveloppe[list[PartantOut]]:
    if repo.get_course(course_id) is None:
        raise HTTPException(status_code=404, detail=f"Course {course_id} introuvable.")
    partants = repo.list_partants_by_course(course_id)
    return Enveloppe(data=[PartantOut.model_validate(p) for p in partants])


@router.get("/partants/{partant_id}", response_model=Enveloppe[PartantOut])
def get_partant(
    partant_id: int,
    repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*LECTURE)),
) -> Enveloppe[PartantOut]:
    partant = repo.get_partant(partant_id)
    if partant is None:
        raise HTTPException(status_code=404, detail=f"Partant {partant_id} introuvable.")
    return Enveloppe(data=PartantOut.model_validate(partant))


@router.patch("/partants/{partant_id}", response_model=Enveloppe[PartantOut])
def update_partant(
    partant_id: int,
    payload: PartantPatch,
    repo: CourseRepository = Depends(get_course_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[PartantOut]:
    ancien = repo.get_partant(partant_id)
    if ancien is None:
        raise HTTPException(status_code=404, detail=f"Partant {partant_id} introuvable.")
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
    audit_repo.enregistrer(
        utilisateur.id, "modification_partant", objet=str(partant_id),
        ancien_etat=serialiser_etat(ancien), nouvel_etat=serialiser_etat(partant),
    )
    return Enveloppe(data=PartantOut.model_validate(partant))


@router.delete("/partants/{partant_id}", response_model=Enveloppe[dict])
def delete_partant(
    partant_id: int,
    repo: CourseRepository = Depends(get_course_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[dict]:
    ancien = repo.get_partant(partant_id)
    if ancien is None:
        raise HTTPException(status_code=404, detail=f"Partant {partant_id} introuvable.")
    repo.delete_partant(partant_id)
    audit_repo.enregistrer(utilisateur.id, "suppression_partant", objet=str(partant_id), ancien_etat=serialiser_etat(ancien))
    return Enveloppe(data={"supprime": True})


@router.post("/courses/{course_id}/resultats", response_model=Enveloppe[ResultatOut], status_code=201)
def create_resultat(
    course_id: int,
    payload: ResultatIn,
    repo: CourseRepository = Depends(get_course_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[ResultatOut]:
    """Toujours une création (get-or-create sur `(course_id, classement)`) : un
    résultat officiel est figé une fois validé, jamais modifié ni supprimé (cf.
    L011 §15, L009 §5.1) — aucun PATCH/DELETE n'est exposé sur cette ressource."""
    if repo.get_course(course_id) is None:
        raise HTTPException(status_code=404, detail=f"Course {course_id} introuvable.")
    if repo.get_partant(payload.partant_id) is None:
        raise HTTPException(status_code=404, detail=f"Partant {payload.partant_id} introuvable.")
    resultat = repo.get_or_create_resultat(Resultat(course_id=course_id, **payload.model_dump()))
    audit_repo.enregistrer(
        utilisateur.id, "creation_resultat", objet=str(resultat.id), nouvel_etat=serialiser_etat(resultat)
    )
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
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*ECRITURE_DONNEES)),
) -> Enveloppe[CoteOut]:
    """Toujours une création : une cote n'est jamais remplacée mais historisée
    (cf. L011 §15) — aucun PATCH/DELETE n'est exposé sur cette ressource."""
    if repo.get_partant(partant_id) is None:
        raise HTTPException(status_code=404, detail=f"Partant {partant_id} introuvable.")
    cote = repo.create_cote(Cote(partant_id=partant_id, **payload.model_dump()))
    audit_repo.enregistrer(utilisateur.id, "creation_cote", objet=str(cote.id), nouvel_etat=serialiser_etat(cote))
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
