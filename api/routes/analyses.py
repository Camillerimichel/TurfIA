"""Routes du domaine Analyses — cf. L007 §4.3, L006 §3, L031.x.

Déclenche la chaîne d'analyse via AnalyseService (aucune logique métier ici, cf.
L016 §2.2) et restitue le classement dans la même forme (`AnalyseDetailOut`) que la
relecture ultérieure d'une analyse déjà persistée.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies.auth import DECLENCHEMENT_ANALYSE, LECTURE, exiger_roles
from api.dependencies.db import get_analyse_repository, get_audit_repository, get_course_repository
from api.dependencies.services import get_analyse_service, get_preparation_service
from api.schemas.analyses import (
    AnalyseAutoIn,
    AnalyseDetailOut,
    AnalyseOut,
    AnalysePartantOut,
    AnalyseTriggerIn,
    ParisOut,
)
from api.schemas.common import Enveloppe
from src.algorithms.classement import PartantClasse
from src.core.audit import serialiser_etat
from src.core.exceptions import ValidationError
from src.models.analyse import AnalysePartant, Pari, Selection
from src.models.course import PartantDetail
from src.models.utilisateur import Utilisateur
from src.repositories.analyse_repository import AnalyseRepository
from src.repositories.audit_repository import AuditRepository
from src.repositories.course_repository import CourseRepository
from src.services.analyse_service import AnalyseService, DonneesPartant
from src.services.preparation_service import PreparationDonneesService

router = APIRouter(tags=["Analyses"])


def _partants_detail_par_id(course_repo: CourseRepository, course_id: int) -> dict[int, PartantDetail]:
    """`{partant_id: PartantDetail}` — pour joindre numéro de course/nom du
    cheval à l'affichage des analyses (cf. L018 §6-7) : `partant_id` seul (clé
    technique) ne permet pas de savoir sur quel cheval parier réellement."""
    return {pd.id: pd for pd in course_repo.list_partants_detail_by_course(course_id)}


def _libelle_partant(partant_id: int, partants_detail: dict[int, PartantDetail]) -> str:
    detail = partants_detail.get(partant_id)
    return f"N°{detail.numero} {detail.cheval_nom}" if detail is not None else f"partant #{partant_id}"


def _resoudre_combinaison(combinaison: str | None, partants_detail: dict[int, PartantDetail]) -> str | None:
    if not combinaison:
        return None
    return " + ".join(_libelle_partant(int(pid), partants_detail) for pid in combinaison.split("-"))


def _partant_classe_vers_out(partant_classe: PartantClasse, partants_detail: dict[int, PartantDetail]) -> AnalysePartantOut:
    """Traduit le résultat en mémoire (`PartantClasse`) vers la forme persistée
    (`AnalysePartantOut`) : `score` = Score TurfIA brut, `confiance` = score final
    après bonus Value Bet / malus risque (cf. L031.6 §3).
    """
    detail = partants_detail.get(partant_classe.partant_id)
    return AnalysePartantOut(
        partant_id=partant_classe.partant_id,
        numero=detail.numero if detail is not None else None,
        cheval_nom=detail.cheval_nom if detail is not None else None,
        score=partant_classe.score_turfia,
        rang=partant_classe.rang,
        consensus=partant_classe.consensus,
        evolution_cote=partant_classe.evolution_cote,
        value_bet=partant_classe.value_bet,
        confiance=partant_classe.score_final,
        categorie=partant_classe.categorie,
    )


def _persistance_vers_out(
    analyse_partant: AnalysePartant, categorie: str | None, partants_detail: dict[int, PartantDetail]
) -> AnalysePartantOut:
    detail = partants_detail.get(analyse_partant.partant_id)
    return AnalysePartantOut(
        partant_id=analyse_partant.partant_id,
        numero=detail.numero if detail is not None else None,
        cheval_nom=detail.cheval_nom if detail is not None else None,
        score=analyse_partant.score,
        rang=analyse_partant.rang,
        consensus=analyse_partant.consensus,
        evolution_cote=analyse_partant.evolution_cote,
        value_bet=analyse_partant.value_bet,
        confiance=analyse_partant.confiance,
        categorie=categorie,
    )


def _pari_vers_out(pari: Pari, partants_detail: dict[int, PartantDetail]) -> ParisOut:
    return ParisOut(
        type_pari=pari.type_pari,
        combinaison=pari.combinaison,
        combinaison_lisible=_resoudre_combinaison(pari.combinaison, partants_detail),
        mise=pari.mise,
        gain_estime=pari.gain_estime,
        roi_estime=pari.roi_estime,
    )


@router.post("/courses/{course_id}/analyses", response_model=Enveloppe[AnalyseDetailOut], status_code=201)
def trigger_analyse(
    course_id: int,
    payload: AnalyseTriggerIn,
    course_repo: CourseRepository = Depends(get_course_repository),
    service: AnalyseService = Depends(get_analyse_service),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*DECLENCHEMENT_ANALYSE)),
) -> Enveloppe[AnalyseDetailOut]:
    if course_repo.get_course(course_id) is None:
        raise HTTPException(status_code=404, detail=f"Course {course_id} introuvable.")

    donnees = [DonneesPartant(**p.model_dump()) for p in payload.partants]
    try:
        resultat = service.analyser_course(
            course_id=course_id,
            version=payload.version,
            partants=donnees,
            sous_risques_course=payload.sous_risques_course,
            mise_reference=payload.mise_reference,
            budget_precedent=payload.budget_precedent,
            perte_precedente=payload.perte_precedente,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    audit_repo.enregistrer(
        utilisateur.id, "declenchement_analyse", objet=str(resultat.analyse.id),
        nouvel_etat=serialiser_etat(resultat.analyse),
    )
    partants_detail = _partants_detail_par_id(course_repo, course_id)
    detail = AnalyseDetailOut(
        analyse=AnalyseOut.model_validate(resultat.analyse),
        partants=[_partant_classe_vers_out(pc, partants_detail) for pc in resultat.partants_classes],
        paris=[_pari_vers_out(p, partants_detail) for p in resultat.paris],
    )
    return Enveloppe(data=detail)


@router.post("/courses/{course_id}/analyses/auto", response_model=Enveloppe[AnalyseDetailOut], status_code=201)
def trigger_analyse_auto(
    course_id: int,
    payload: AnalyseAutoIn,
    course_repo: CourseRepository = Depends(get_course_repository),
    preparation: PreparationDonneesService = Depends(get_preparation_service),
    service: AnalyseService = Depends(get_analyse_service),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*DECLENCHEMENT_ANALYSE)),
) -> Enveloppe[AnalyseDetailOut]:
    """Referme la boucle collecte -> analyse : les sous-scores (marché, forme) et
    le risque sont calculés à partir des données déjà collectées
    (cf. PreparationDonneesService), sans saisie manuelle. Vise toujours la
    version suivante (cf. AnalyseService.prochaine_version) : peut être
    déclenchée à tout moment, y compris après une analyse déjà existante
    (ex. automatisation horaire), sans jamais échouer en conflit de version.
    """
    if course_repo.get_course(course_id) is None:
        raise HTTPException(status_code=404, detail=f"Course {course_id} introuvable.")

    try:
        donnees_partants, sous_risques_course = preparation.preparer_donnees_partants(course_id)
        resultat = service.analyser_course(
            course_id=course_id,
            version=service.prochaine_version(course_id),
            partants=donnees_partants,
            sous_risques_course=sous_risques_course,
            mise_reference=payload.mise_reference,
            budget_precedent=payload.budget_precedent,
            perte_precedente=payload.perte_precedente,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    audit_repo.enregistrer(
        utilisateur.id, "declenchement_analyse", objet=str(resultat.analyse.id),
        nouvel_etat=serialiser_etat(resultat.analyse),
    )
    partants_detail = _partants_detail_par_id(course_repo, course_id)
    detail = AnalyseDetailOut(
        analyse=AnalyseOut.model_validate(resultat.analyse),
        partants=[_partant_classe_vers_out(pc, partants_detail) for pc in resultat.partants_classes],
        paris=[_pari_vers_out(p, partants_detail) for p in resultat.paris],
    )
    return Enveloppe(data=detail)


@router.get("/courses/{course_id}/analyses", response_model=Enveloppe[list[AnalyseOut]])
def list_analyses(
    course_id: int,
    repo: AnalyseRepository = Depends(get_analyse_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*LECTURE)),
) -> Enveloppe[list[AnalyseOut]]:
    analyses = [AnalyseOut.model_validate(a) for a in repo.list_analyses_by_course(course_id)]
    return Enveloppe(data=analyses)


@router.get("/analyses/{analyse_id}", response_model=Enveloppe[AnalyseDetailOut])
def get_analyse(
    analyse_id: int,
    repo: AnalyseRepository = Depends(get_analyse_repository),
    course_repo: CourseRepository = Depends(get_course_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*LECTURE)),
) -> Enveloppe[AnalyseDetailOut]:
    analyse = repo.get_analyse(analyse_id)
    if analyse is None:
        raise HTTPException(status_code=404, detail=f"Analyse {analyse_id} introuvable.")

    analyse_partants = repo.list_analyse_partants(analyse_id)
    selections: list[Selection] = repo.list_selections_by_analyse(analyse_id)
    categorie_par_partant = {s.partant_id: s.categorie for s in selections}
    paris = repo.list_paris_by_analyse(analyse_id)
    partants_detail = _partants_detail_par_id(course_repo, analyse.course_id)

    detail = AnalyseDetailOut(
        analyse=AnalyseOut.model_validate(analyse),
        partants=[
            _persistance_vers_out(ap, categorie_par_partant.get(ap.partant_id), partants_detail)
            for ap in analyse_partants
        ],
        paris=[_pari_vers_out(p, partants_detail) for p in paris],
    )
    return Enveloppe(data=detail)
