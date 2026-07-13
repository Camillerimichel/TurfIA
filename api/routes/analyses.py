"""Routes du domaine Analyses — cf. L007 §4.3, L006 §3, L031.x.

Déclenche la chaîne d'analyse via AnalyseService (aucune logique métier ici, cf.
L016 §2.2) et restitue le classement dans la même forme (`AnalyseDetailOut`) que la
relecture ultérieure d'une analyse déjà persistée.
"""

from __future__ import annotations

import itertools

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies.auth import DECLENCHEMENT_ANALYSE, LECTURE, exiger_roles
from api.dependencies.db import (
    get_analyse_repository,
    get_audit_repository,
    get_course_repository,
    get_referentiel_repository,
)
from api.dependencies.services import (
    get_analyse_service,
    get_controle_roi_service,
    get_ia_analyse_service,
    get_preparation_service,
)
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
from src.core.exceptions import AnalysisError, ValidationError
from src.models.analyse import AnalysePartant, Pari, Selection
from src.models.course import PartantDetail
from src.models.utilisateur import Utilisateur
from src.repositories.analyse_repository import AnalyseRepository
from src.repositories.audit_repository import AuditRepository
from src.repositories.course_repository import CourseRepository
from src.repositories.referentiel_repository import ReferentielRepository
from src.services.analyse_service import AnalyseService, DonneesPartant
from src.services.controle_roi_service import ControleRoiService
from src.services.ia_analyse_service import ContexteCourseIa, ContextePartantIa, IaAnalyseService
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


def _sous_combinaisons_quinte(
    combinaison: str, mise: float, partants_detail: dict[int, PartantDetail]
) -> tuple[list[str], float] | None:
    """Un ticket Quinté Flexi couvre TOUTES les combinaisons de 5 chevaux parmi
    la sélection retenue (Bases + Chances régulières + Outsider + Tocard
    éventuel, cf. `construire_paris`/`_construire_selection_quinte`) — pas une
    seule combinaison. `Pari.combinaison` ne stocke que le pool de chevaux
    sélectionnés ; sans cette expansion, rien n'indiquait quelles combinaisons
    précises sont réellement jouées (même logique que `ControleRoiService.
    calculer_gains_pari`, qui les énumère déjà pour calculer les gains réels —
    ici, c'est pour l'affichage). Retourne `None` si la sélection compte déjà
    exactement 5 chevaux (une seule combinaison, `combinaison_lisible` suffit).
    """
    partant_ids = [int(pid) for pid in combinaison.split("-")]
    if len(partant_ids) <= 5:
        return None
    sous_combinaisons = list(itertools.combinations(partant_ids, 5))
    libelles = [
        " + ".join(_libelle_partant(pid, partants_detail) for pid in combo) for combo in sous_combinaisons
    ]
    return libelles, round(mise / len(sous_combinaisons), 2)


def _construire_contexte_ia(
    course_id: int,
    donnees_partants: list[DonneesPartant],
    course_repo: CourseRepository,
    referentiel_repo: ReferentielRepository,
) -> tuple[ContexteCourseIa, list[ContextePartantIa]]:
    """Assemble le contexte transmis à l'IA — mêmes données que le moteur
    classique (cf. `CourseRepository.list_partants_detail_by_course`, déjà
    sans appel N+1), pas moins."""
    course = course_repo.get_course(course_id)
    reunion = course_repo.get_reunion(course.reunion_id)
    hippodrome = referentiel_repo.get_hippodrome(reunion.hippodrome_id)
    discipline = referentiel_repo.get_discipline(course.discipline_id) if course.discipline_id else None
    distance = referentiel_repo.get_distance(course.distance_id) if course.distance_id else None
    etat_piste = referentiel_repo.get_etat_piste(course.etat_piste_id) if course.etat_piste_id else None

    contexte_course = ContexteCourseIa(
        hippodrome_nom=hippodrome.nom if hippodrome is not None else "inconnu",
        discipline=discipline.libelle if discipline is not None else None,
        distance_metres=distance.distance if distance is not None else None,
        allocation=course.allocation,
        terrain=etat_piste.libelle if etat_piste is not None else None,
    )

    sous_scores_par_partant = {dp.partant_id: dp.sous_scores for dp in donnees_partants}
    contextes_partants = [
        ContextePartantIa(
            partant_id=pd.id,
            numero=pd.numero,
            cheval_nom=pd.cheval_nom,
            cote=pd.derniere_cote,
            musique=pd.musique,
            jockey_nom=pd.jockey_nom,
            entraineur_nom=pd.entraineur_nom,
            sous_scores=sous_scores_par_partant.get(pd.id, {}),
        )
        for pd in course_repo.list_partants_detail_by_course(course_id)
        if pd.id in sous_scores_par_partant
    ]
    return contexte_course, contextes_partants


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
    sous_combinaisons = None
    mise_par_combinaison = None
    if pari.type_pari == "Quinté Flexi" and pari.combinaison:
        resultat = _sous_combinaisons_quinte(pari.combinaison, pari.mise, partants_detail)
        if resultat is not None:
            sous_combinaisons, mise_par_combinaison = resultat

    return ParisOut(
        type_pari=pari.type_pari,
        combinaison=pari.combinaison,
        combinaison_lisible=_resoudre_combinaison(pari.combinaison, partants_detail),
        sous_combinaisons=sous_combinaisons,
        mise_par_combinaison=mise_par_combinaison,
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
    course = course_repo.get_course(course_id)
    if course is None:
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
            quinte=course.quinte,
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
    course = course_repo.get_course(course_id)
    if course is None:
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
            quinte=course.quinte,
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


@router.post("/courses/{course_id}/analyses/ia", response_model=Enveloppe[AnalyseDetailOut], status_code=201)
def trigger_analyse_ia(
    course_id: int,
    payload: AnalyseAutoIn,
    course_repo: CourseRepository = Depends(get_course_repository),
    referentiel_repo: ReferentielRepository = Depends(get_referentiel_repository),
    preparation: PreparationDonneesService = Depends(get_preparation_service),
    ia_service: IaAnalyseService = Depends(get_ia_analyse_service),
    service: AnalyseService = Depends(get_analyse_service),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*DECLENCHEMENT_ANALYSE)),
) -> Enveloppe[AnalyseDetailOut]:
    """Analyse IA à la demande (Claude Sonnet 5, cf. retour utilisateur du
    2026-07-12) : alimente les familles de score "value"/"contexte" (jamais
    calculées par aucune autre voie) puis referme la même chaîne que `/auto`.
    Aucune persistance tant que l'IA n'a pas répondu avec succès — cf.
    `IaAnalyseService`, principe "pas de score fabriqué"."""
    course = course_repo.get_course(course_id)
    if course is None:
        raise HTTPException(status_code=404, detail=f"Course {course_id} introuvable.")

    donnees_partants, sous_risques_course = preparation.preparer_donnees_partants(course_id)
    contexte_course, contextes_partants = _construire_contexte_ia(
        course_id, donnees_partants, course_repo, referentiel_repo
    )
    try:
        resultat_ia = ia_service.analyser(contexte_course, contextes_partants)
    except AnalysisError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    for dp in donnees_partants:
        valeur, contexte = resultat_ia.scores_par_partant[dp.partant_id]
        dp.sous_scores["value"] = valeur
        dp.sous_scores["contexte"] = contexte

    try:
        resultat = service.analyser_course(
            course_id=course_id,
            version=service.prochaine_version(course_id),
            partants=donnees_partants,
            sous_risques_course=sous_risques_course,
            mise_reference=payload.mise_reference,
            budget_precedent=payload.budget_precedent,
            perte_precedente=payload.perte_precedente,
            commentaire=resultat_ia.synthese,
            source="ia",
            quinte=course.quinte,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    audit_repo.enregistrer(
        utilisateur.id, "declenchement_analyse_ia", objet=str(resultat.analyse.id),
        nouvel_etat=serialiser_etat(resultat.analyse),
    )
    partants_detail = _partants_detail_par_id(course_repo, course_id)
    detail = AnalyseDetailOut(
        analyse=AnalyseOut.model_validate(resultat.analyse),
        partants=[_partant_classe_vers_out(pc, partants_detail) for pc in resultat.partants_classes],
        paris=[_pari_vers_out(p, partants_detail) for p in resultat.paris],
    )
    return Enveloppe(data=detail)


def _analyses_avec_selection(repo: AnalyseRepository, course_id: int, analyses: list) -> list[AnalyseOut]:
    """Marque `selectionnee` sur l'analyse qui compte réellement pour cette
    course (sélection manuelle si elle existe, sinon dernière version, cf.
    `AnalyseRepository.get_analyse_selectionnee_id`) — pas un champ de
    `Analyse` (pas une colonne DB), calculé ici après `model_validate()`."""
    selectionnee_id = repo.get_analyse_selectionnee_id(course_id) if analyses else None
    resultat = []
    for a in analyses:
        out = AnalyseOut.model_validate(a)
        out.selectionnee = a.id == selectionnee_id
        resultat.append(out)
    return resultat


@router.get("/courses/{course_id}/analyses", response_model=Enveloppe[list[AnalyseOut]])
def list_analyses(
    course_id: int,
    repo: AnalyseRepository = Depends(get_analyse_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*LECTURE)),
) -> Enveloppe[list[AnalyseOut]]:
    analyses = repo.list_analyses_by_course(course_id)
    return Enveloppe(data=_analyses_avec_selection(repo, course_id, analyses))


@router.post(
    "/courses/{course_id}/analyses/{analyse_id}/selectionner", response_model=Enveloppe[list[AnalyseOut]]
)
def selectionner_analyse(
    course_id: int,
    analyse_id: int,
    course_repo: CourseRepository = Depends(get_course_repository),
    analyse_repo: AnalyseRepository = Depends(get_analyse_repository),
    controle_roi_service: ControleRoiService = Depends(get_controle_roi_service),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*DECLENCHEMENT_ANALYSE)),
) -> Enveloppe[list[AnalyseOut]]:
    """Fige manuellement quelle analyse compte pour l'historique/ROI de cette
    course (retour utilisateur, 2026-07-12), au lieu du calcul automatique
    MAX(version). Si la version choisie n'a pas encore de contrôle ROI et que
    la course est arrivée, le calcule aussitôt (même confirmation utilisateur)."""
    if course_repo.get_course(course_id) is None:
        raise HTTPException(status_code=404, detail=f"Course {course_id} introuvable.")
    analyse = analyse_repo.get_analyse(analyse_id)
    if analyse is None or analyse.course_id != course_id:
        raise HTTPException(status_code=404, detail=f"Analyse {analyse_id} introuvable pour la course {course_id}.")

    analyse_repo.definir_selection(course_id, analyse_id)
    controle_roi_service.calculer_controle_pour_analyse(analyse_id)
    audit_repo.enregistrer(utilisateur.id, "selection_analyse", objet=str(analyse_id))

    analyses = analyse_repo.list_analyses_by_course(course_id)
    return Enveloppe(data=_analyses_avec_selection(analyse_repo, course_id, analyses))


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
