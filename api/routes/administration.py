"""Routes du module Administration — cf. L018 §10.

Toutes réservées au rôle Administrateur (`ADMINISTRATION`) : journaux, lancement
d'automatisations, sauvegardes, versions, paramètres, supervision. Chaque action
sensible est journalisée dans `audit` avec l'identité de l'opérateur (cf. L018
§10.1) ; la confirmation explicite avant déclenchement est de la responsabilité
du JS côté client (`window.confirm`, cf. `html/static/js/administration.js`).
"""

from __future__ import annotations

import subprocess
from collections import deque
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies.auth import ADMINISTRATION, exiger_roles
from api.dependencies.db import (
    get_audit_repository,
    get_journal_repository,
    get_parametre_repository,
    get_tache_repository,
    get_version_repository,
)
from api.dependencies.services import (
    get_automatisation_service,
    get_collecte_service,
    get_controle_roi_service,
    get_statistique_service,
    get_supervision_service,
)
from api.schemas.administration import (
    ErreurCourseOut,
    EtatSupervisionOut,
    JournalCronOut,
    JournalOut,
    ParametreOut,
    ParametrePatchIn,
    RapportAnalyseJourOut,
    TacheCronOut,
    TacheOut,
    VersionOut,
)
from api.schemas.common import Enveloppe
from src.core.audit import serialiser_etat
from src.core.config import Settings, get_settings
from src.models.utilisateur import Utilisateur
from src.repositories.audit_repository import AuditRepository
from src.repositories.journal_repository import JournalRepository
from src.repositories.parametre_repository import ParametreRepository
from src.repositories.tache_repository import TacheRepository
from src.repositories.version_repository import VersionRepository
from src.services.automatisation_service import AutomatisationService
from src.services.collecte_service import CollecteService
from src.services.controle_roi_service import ControleRoiService
from src.services.statistique_service import StatistiqueService
from src.services.supervision_service import SupervisionService

router = APIRouter(prefix="/administration", tags=["Administration"])

RACINE_PROJET = Path(__file__).resolve().parent.parent.parent

# Tâches quotidiennes connues (cf. scripts/rafraichir_et_analyser_jour.py,
# automations/launchd/) — liste fixe plutôt qu'un registre générique, un seul
# script planifié existant à ce jour (cf. L018 §10, tableau de bord Cron).
TACHES_QUOTIDIENNES: list[tuple[str, str]] = [
    ("collecte_programme_jour", "Collecte du programme du jour"),
    ("analyse_courses_jour", "Analyse des courses du jour"),
]

# Les deux étapes de scripts/rafraichir_et_analyser_jour.py écrivent dans les
# mêmes fichiers (cf. automations/launchd/com.turfia.rafraichir-analyser.plist,
# StandardOutPath/StandardErrorPath) — un seul journal partagé, pas un par tâche.
CHEMIN_JOURNAL_CRON = RACINE_PROJET / "logs" / "rafraichir_et_analyser.log"
CHEMIN_JOURNAL_CRON_ERREURS = RACINE_PROJET / "logs" / "rafraichir_et_analyser.err.log"
NB_LIGNES_JOURNAL_CRON = 200  # pas d'archive (cf. L018 §10) : juste la fin du fichier courant


def _lire_dernieres_lignes(chemin: Path, n: int) -> str:
    if not chemin.exists():
        return ""
    with chemin.open(encoding="utf-8", errors="replace") as fichier:
        return "".join(deque(fichier, maxlen=n))


# -- 2.0 Tableau de bord Cron -----------------------------------------------------


@router.get("/cron", response_model=Enveloppe[list[TacheCronOut]])
def list_cron(
    tache_repo: TacheRepository = Depends(get_tache_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*ADMINISTRATION)),
) -> Enveloppe[list[TacheCronOut]]:
    resultat = [
        TacheCronOut(
            nom=nom,
            libelle=libelle,
            derniere_tache=(
                TacheOut.model_validate(derniere) if (derniere := tache_repo.get_derniere_par_nom(nom)) else None
            ),
        )
        for nom, libelle in TACHES_QUOTIDIENNES
    ]
    return Enveloppe(data=resultat)


@router.get("/cron/journal", response_model=Enveloppe[JournalCronOut])
def get_journal_cron(
    _utilisateur: Utilisateur = Depends(exiger_roles(*ADMINISTRATION)),
) -> Enveloppe[JournalCronOut]:
    return Enveloppe(
        data=JournalCronOut(
            sortie=_lire_dernieres_lignes(CHEMIN_JOURNAL_CRON, NB_LIGNES_JOURNAL_CRON),
            erreurs=_lire_dernieres_lignes(CHEMIN_JOURNAL_CRON_ERREURS, NB_LIGNES_JOURNAL_CRON),
        )
    )


# -- 2.1 Journaux --------------------------------------------------------------


@router.get("/journaux", response_model=Enveloppe[list[JournalOut]])
def list_journaux(
    niveau: str | None = None,
    composant: str | None = None,
    date_debut: date | None = None,
    date_fin: date | None = None,
    limite: int = 200,
    repo: JournalRepository = Depends(get_journal_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*ADMINISTRATION)),
) -> Enveloppe[list[JournalOut]]:
    journaux = repo.lister(niveau, composant, date_debut, date_fin, limite)
    return Enveloppe(data=[JournalOut.model_validate(j) for j in journaux])


# -- 2.2 Lancer une automatisation ----------------------------------------------


@router.get("/automatisations", response_model=Enveloppe[list[TacheOut]])
def list_automatisations(
    limite: int = 20,
    repo: TacheRepository = Depends(get_tache_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*ADMINISTRATION)),
) -> Enveloppe[list[TacheOut]]:
    return Enveloppe(data=[TacheOut.model_validate(t) for t in repo.lister(categorie="automatisation", limite=limite)])


@router.post("/automatisations/collecte", response_model=Enveloppe[dict])
def declencher_collecte(
    service: CollecteService = Depends(get_collecte_service),
    tache_repo: TacheRepository = Depends(get_tache_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*ADMINISTRATION)),
) -> Enveloppe[dict]:
    tache = tache_repo.demarrer("collecte_programme_jour", categorie="automatisation")
    try:
        rapport = service.collecter_programme_du_jour(date.today())
    except Exception as exc:
        tache_repo.terminer(tache.id, "echec", commentaire=str(exc)[:2000])
        raise
    tache_repo.terminer(
        tache.id, "succes",
        commentaire=f"{rapport.nb_reunions} réunion(s), {rapport.nb_courses} course(s), {rapport.nb_partants} partant(s)",
    )
    audit_repo.enregistrer(utilisateur.id, "automatisation_collecte", objet=str(tache.id))
    return Enveloppe(data={
        "nb_reunions": rapport.nb_reunions,
        "nb_courses": rapport.nb_courses,
        "nb_partants": rapport.nb_partants,
        "erreurs": rapport.erreurs,
    })


@router.post("/automatisations/analyse-jour", response_model=Enveloppe[RapportAnalyseJourOut])
def declencher_analyse_jour(
    version: int = 1,
    service: AutomatisationService = Depends(get_automatisation_service),
    tache_repo: TacheRepository = Depends(get_tache_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*ADMINISTRATION)),
) -> Enveloppe[RapportAnalyseJourOut]:
    tache = tache_repo.demarrer("analyse_courses_jour", categorie="automatisation")
    try:
        rapport = service.analyser_courses_du_jour(date.today(), version)
    except Exception as exc:
        tache_repo.terminer(tache.id, "echec", commentaire=str(exc)[:2000])
        raise
    statut = "succes" if rapport.nb_erreurs == 0 else "echec"
    tache_repo.terminer(
        tache.id, statut,
        commentaire=(
            f"{rapport.nb_courses} course(s), {rapport.nb_deja_analysees} déjà à jour, "
            f"{rapport.nb_erreurs} erreur(s)"
        ),
    )
    audit_repo.enregistrer(utilisateur.id, "automatisation_analyse_jour", objet=str(tache.id))
    return Enveloppe(data=RapportAnalyseJourOut(
        nb_courses=rapport.nb_courses,
        nb_erreurs=rapport.nb_erreurs,
        nb_deja_analysees=rapport.nb_deja_analysees,
        erreurs=[ErreurCourseOut(course_id=cid, message=msg) for cid, msg in rapport.erreurs],
    ))


@router.post("/automatisations/statistiques", response_model=Enveloppe[dict])
def declencher_statistiques(
    controle_roi_service: ControleRoiService = Depends(get_controle_roi_service),
    statistique_service: StatistiqueService = Depends(get_statistique_service),
    tache_repo: TacheRepository = Depends(get_tache_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*ADMINISTRATION)),
) -> Enveloppe[dict]:
    tache = tache_repo.demarrer("calcul_statistiques", categorie="automatisation")
    try:
        controles = controle_roi_service.calculer_controles_manquants()
        resume = statistique_service.calculer_toutes()
    except Exception as exc:
        tache_repo.terminer(tache.id, "echec", commentaire=str(exc)[:2000])
        raise
    tache_repo.terminer(tache.id, "succes", commentaire=f"{len(controles)} contrôle(s) ROI, tables : {resume}")
    audit_repo.enregistrer(utilisateur.id, "automatisation_statistiques", objet=str(tache.id))
    return Enveloppe(data={"nb_controles_roi": len(controles), "tables": resume})


# -- 2.3 Vérifier les sauvegardes ------------------------------------------------


@router.get("/sauvegardes", response_model=Enveloppe[list[TacheOut]])
def list_sauvegardes(
    limite: int = 20,
    repo: TacheRepository = Depends(get_tache_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*ADMINISTRATION)),
) -> Enveloppe[list[TacheOut]]:
    return Enveloppe(data=[TacheOut.model_validate(t) for t in repo.lister(categorie="sauvegarde", limite=limite)])


@router.post("/sauvegardes", response_model=Enveloppe[TacheOut])
def declencher_sauvegarde(
    tache_repo: TacheRepository = Depends(get_tache_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    settings: Settings = Depends(get_settings),
    utilisateur: Utilisateur = Depends(exiger_roles(*ADMINISTRATION)),
) -> Enveloppe[TacheOut]:
    from scripts.sauvegarder_base import executer_sauvegarde

    tache = tache_repo.demarrer("sauvegarde_base", categorie="sauvegarde")
    try:
        chemin, taille = executer_sauvegarde(settings.database_url, settings.chemin_sauvegardes)
    except subprocess.CalledProcessError as exc:
        tache_repo.terminer(tache.id, "echec", commentaire=(exc.stderr or b"").decode(errors="replace")[:2000])
        raise HTTPException(status_code=500, detail="La sauvegarde a échoué.") from exc
    tache = tache_repo.terminer(tache.id, "succes", commentaire=f"{chemin} ({taille} octets)")
    audit_repo.enregistrer(utilisateur.id, "sauvegarde_manuelle", objet=str(tache.id))
    return Enveloppe(data=TacheOut.model_validate(tache))


# -- 2.4 Consulter les versions ---------------------------------------------------


@router.get("/versions", response_model=Enveloppe[list[VersionOut]])
def list_versions(
    limite: int = 20,
    repo: VersionRepository = Depends(get_version_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*ADMINISTRATION)),
) -> Enveloppe[list[VersionOut]]:
    return Enveloppe(data=[VersionOut.model_validate(v) for v in repo.lister(limite)])


# -- 2.5 Gérer les paramètres ------------------------------------------------------


@router.get("/parametres", response_model=Enveloppe[list[ParametreOut]])
def list_parametres(
    repo: ParametreRepository = Depends(get_parametre_repository),
    _utilisateur: Utilisateur = Depends(exiger_roles(*ADMINISTRATION)),
) -> Enveloppe[list[ParametreOut]]:
    return Enveloppe(data=[ParametreOut.model_validate(p) for p in repo.lister()])


@router.patch("/parametres/{cle}", response_model=Enveloppe[ParametreOut])
def update_parametre(
    cle: str,
    payload: ParametrePatchIn,
    repo: ParametreRepository = Depends(get_parametre_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository),
    utilisateur: Utilisateur = Depends(exiger_roles(*ADMINISTRATION)),
) -> Enveloppe[ParametreOut]:
    ancien = repo.get_parametre(cle)
    if ancien is None:
        raise HTTPException(status_code=404, detail=f"Paramètre '{cle}' introuvable.")
    parametre = repo.update_parametre(cle, payload.valeur)
    audit_repo.enregistrer(
        utilisateur.id, "modification_parametre", objet=cle,
        ancien_etat=serialiser_etat(ancien), nouvel_etat=serialiser_etat(parametre),
    )
    return Enveloppe(data=ParametreOut.model_validate(parametre))


# -- 2.6 Contrôler la supervision --------------------------------------------------


@router.get("/supervision", response_model=Enveloppe[EtatSupervisionOut])
def get_supervision(
    service: SupervisionService = Depends(get_supervision_service),
    _utilisateur: Utilisateur = Depends(exiger_roles(*ADMINISTRATION)),
) -> Enveloppe[EtatSupervisionOut]:
    return Enveloppe(data=EtatSupervisionOut.model_validate(service.etat()))
