"""Routes du domaine Analyses — cf. L007 §4.3, L006 §3, L031.x.

Déclenche la chaîne d'analyse via AnalyseService (aucune logique métier ici, cf.
L016 §2.2) et restitue le classement dans la même forme (`AnalyseDetailOut`) que la
relecture ultérieure d'une analyse déjà persistée.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies.db import get_analyse_repository, get_course_repository
from api.dependencies.services import get_analyse_service
from api.schemas.analyses import AnalyseDetailOut, AnalyseOut, AnalysePartantOut, AnalyseTriggerIn, ParisOut
from api.schemas.common import Enveloppe
from src.algorithms.classement import PartantClasse
from src.core.exceptions import ValidationError
from src.models.analyse import AnalysePartant, Selection
from src.repositories.analyse_repository import AnalyseRepository
from src.repositories.course_repository import CourseRepository
from src.services.analyse_service import AnalyseService, DonneesPartant

router = APIRouter(tags=["Analyses"])


def _partant_classe_vers_out(partant_classe: PartantClasse) -> AnalysePartantOut:
    """Traduit le résultat en mémoire (`PartantClasse`) vers la forme persistée
    (`AnalysePartantOut`) : `score` = Score TurfIA brut, `confiance` = score final
    après bonus Value Bet / malus risque (cf. L031.6 §3).
    """
    return AnalysePartantOut(
        partant_id=partant_classe.partant_id,
        score=partant_classe.score_turfia,
        rang=partant_classe.rang,
        consensus=partant_classe.consensus,
        evolution_cote=partant_classe.evolution_cote,
        value_bet=partant_classe.value_bet,
        confiance=partant_classe.score_final,
        categorie=partant_classe.categorie,
    )


def _persistance_vers_out(analyse_partant: AnalysePartant, categorie: str | None) -> AnalysePartantOut:
    return AnalysePartantOut(
        partant_id=analyse_partant.partant_id,
        score=analyse_partant.score,
        rang=analyse_partant.rang,
        consensus=analyse_partant.consensus,
        evolution_cote=analyse_partant.evolution_cote,
        value_bet=analyse_partant.value_bet,
        confiance=analyse_partant.confiance,
        categorie=categorie,
    )


@router.post("/courses/{course_id}/analyses", response_model=Enveloppe[AnalyseDetailOut], status_code=201)
def trigger_analyse(
    course_id: int,
    payload: AnalyseTriggerIn,
    course_repo: CourseRepository = Depends(get_course_repository),
    service: AnalyseService = Depends(get_analyse_service),
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

    detail = AnalyseDetailOut(
        analyse=AnalyseOut.model_validate(resultat.analyse),
        partants=[_partant_classe_vers_out(pc) for pc in resultat.partants_classes],
        paris=[ParisOut.model_validate(p) for p in resultat.paris],
    )
    return Enveloppe(data=detail)


@router.get("/courses/{course_id}/analyses", response_model=Enveloppe[list[AnalyseOut]])
def list_analyses(
    course_id: int, repo: AnalyseRepository = Depends(get_analyse_repository)
) -> Enveloppe[list[AnalyseOut]]:
    analyses = [AnalyseOut.model_validate(a) for a in repo.list_analyses_by_course(course_id)]
    return Enveloppe(data=analyses)


@router.get("/analyses/{analyse_id}", response_model=Enveloppe[AnalyseDetailOut])
def get_analyse(
    analyse_id: int, repo: AnalyseRepository = Depends(get_analyse_repository)
) -> Enveloppe[AnalyseDetailOut]:
    analyse = repo.get_analyse(analyse_id)
    if analyse is None:
        raise HTTPException(status_code=404, detail=f"Analyse {analyse_id} introuvable.")

    analyse_partants = repo.list_analyse_partants(analyse_id)
    selections: list[Selection] = repo.list_selections_by_analyse(analyse_id)
    categorie_par_partant = {s.partant_id: s.categorie for s in selections}
    paris = repo.list_paris_by_analyse(analyse_id)

    detail = AnalyseDetailOut(
        analyse=AnalyseOut.model_validate(analyse),
        partants=[_persistance_vers_out(ap, categorie_par_partant.get(ap.partant_id)) for ap in analyse_partants],
        paris=[ParisOut.model_validate(p) for p in paris],
    )
    return Enveloppe(data=detail)
