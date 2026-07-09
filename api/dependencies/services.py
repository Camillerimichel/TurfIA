"""Dépendances FastAPI vers les services applicatifs — cf. L015 §7."""

from __future__ import annotations

from collections.abc import Generator
from datetime import datetime, timezone

from fastapi import Depends

from api.dependencies.db import (
    get_analyse_repository,
    get_audit_repository,
    get_course_repository,
    get_parametre_repository,
    get_referentiel_repository,
    get_statistique_repository,
    get_tache_repository,
    get_utilisateur_repository,
)
from src.collecte.canalturf.client import CanalturfClient
from src.collecte.pmu.client import PMUClient
from src.collecte.zoneturf.client import ZoneTurfClient
from src.core.config import Settings, get_settings
from src.repositories.analyse_repository import AnalyseRepository
from src.repositories.audit_repository import AuditRepository
from src.repositories.course_repository import CourseRepository
from src.repositories.parametre_repository import ParametreRepository
from src.repositories.referentiel_repository import ReferentielRepository
from src.repositories.tache_repository import TacheRepository
from src.repositories.utilisateur_repository import UtilisateurRepository
from src.services.analyse_service import AnalyseService
from src.services.auth_service import AuthService
from src.services.automatisation_service import AutomatisationService
from src.services.collecte_service import CollecteService
from src.services.consensus_presse_service import ConsensusPresseService
from src.services.controle_roi_service import ControleRoiService
from src.services.preparation_service import PreparationDonneesService
from src.services.statistique_service import StatistiqueService
from src.services.supervision_service import SupervisionService
from src.repositories.statistique_repository import StatistiqueRepository

# Démarrage du processus (cf. L018 §10 « contrôler la supervision ») — fixé une
# seule fois à l'import, pas dans `api/main.py` pour éviter tout import
# circulaire (main.py importe les routeurs, qui importent ce module).
DEMARRAGE_PROCESSUS = datetime.now(timezone.utc)


def get_analyse_service(
    repo: AnalyseRepository = Depends(get_analyse_repository),
    parametres: ParametreRepository = Depends(get_parametre_repository),
) -> AnalyseService:
    poids_score = parametres.obtenir_poids("poids_score") or None
    poids_risque = parametres.obtenir_poids("poids_risque") or None
    return AnalyseService(repo, poids_score=poids_score, poids_risque=poids_risque)


def get_auth_service(
    utilisateurs: UtilisateurRepository = Depends(get_utilisateur_repository),
    audit: AuditRepository = Depends(get_audit_repository),
    settings: Settings = Depends(get_settings),
) -> AuthService:
    return AuthService(utilisateurs, audit, settings.session_duree_minutes)


def get_consensus_presse_service() -> Generator[ConsensusPresseService, None, None]:
    with CanalturfClient() as canalturf_client, ZoneTurfClient() as zoneturf_client:
        yield ConsensusPresseService(canalturf_client, zoneturf_client)


def get_preparation_service(
    repo: CourseRepository = Depends(get_course_repository),
    statistiques: StatistiqueRepository = Depends(get_statistique_repository),
    presse: ConsensusPresseService = Depends(get_consensus_presse_service),
) -> PreparationDonneesService:
    return PreparationDonneesService(repo, statistiques, presse)


def get_automatisation_service(
    course_repo: CourseRepository = Depends(get_course_repository),
    preparation: PreparationDonneesService = Depends(get_preparation_service),
    analyse_service: AnalyseService = Depends(get_analyse_service),
) -> AutomatisationService:
    return AutomatisationService(course_repo, preparation, analyse_service)


def get_collecte_service(
    referentiel_repo: ReferentielRepository = Depends(get_referentiel_repository),
    course_repo: CourseRepository = Depends(get_course_repository),
) -> Generator[CollecteService, None, None]:
    with PMUClient() as pmu_client:
        yield CollecteService(pmu_client, referentiel_repo, course_repo)


def get_controle_roi_service(
    analyse_repo: AnalyseRepository = Depends(get_analyse_repository),
    course_repo: CourseRepository = Depends(get_course_repository),
) -> Generator[ControleRoiService, None, None]:
    with PMUClient() as pmu_client:
        yield ControleRoiService(pmu_client, analyse_repo, course_repo)


def get_statistique_service(
    repo: StatistiqueRepository = Depends(get_statistique_repository),
) -> StatistiqueService:
    return StatistiqueService(repo)


def get_supervision_service(
    tache_repo: TacheRepository = Depends(get_tache_repository),
    settings: Settings = Depends(get_settings),
) -> SupervisionService:
    return SupervisionService(settings.database_url, settings.chemin_sauvegardes, tache_repo, DEMARRAGE_PROCESSUS)
