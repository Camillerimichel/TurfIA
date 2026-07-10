import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "postgresql://dummy@localhost/dummy")
os.environ.setdefault("SECRET_KEY", "dummy")
# Pas de base réelle en test : évite que chaque log WARNING+ tente une connexion
# psycopg réelle via DbLogHandler (cf. api/main.py, src/core/log_db_handler.py).
os.environ.setdefault("LOG_JOURNAL_DB_ACTIF", "false")

from api.dependencies.auth import get_utilisateur_courant  # noqa: E402
from api.dependencies.db import (  # noqa: E402
    get_analyse_repository,
    get_audit_repository,
    get_course_repository,
    get_historique_repository,
    get_journal_repository,
    get_parametre_repository,
    get_referentiel_repository,
    get_statistique_repository,
    get_tache_repository,
    get_version_repository,
)
from api.dependencies.services import (  # noqa: E402
    get_analyse_service,
    get_auth_service,
    get_automatisation_service,
    get_collecte_service,
    get_controle_roi_service,
    get_preparation_service,
    get_statistique_service,
    get_supervision_service,
)
from api.main import app  # noqa: E402
from src.models.referentiels import Hippodrome  # noqa: E402
from src.models.utilisateur import Role, Utilisateur  # noqa: E402
from src.services.analyse_service import AnalyseService  # noqa: E402
from src.services.auth_service import AuthService  # noqa: E402
from src.services.automatisation_service import AutomatisationService  # noqa: E402
from src.services.preparation_service import PreparationDonneesService  # noqa: E402
from src.services.statistique_service import StatistiqueService  # noqa: E402
from tests.integration.fakes import (  # noqa: E402
    FakeAnalyseRepository,
    FakeAuditRepository,
    FakeConsensusPresseService,
    FakeCollecteService,
    FakeControleRoiService,
    FakeCourseRepository,
    FakeHistoriqueRepository,
    FakeJournalRepository,
    FakeParametreRepository,
    FakeReferentielRepository,
    FakeStatistiqueRepository,
    FakeSupervisionService,
    FakeTacheRepository,
    FakeUtilisateurRepository,
    FakeVersionRepository,
)


@pytest.fixture
def repos():
    referentiel_repo = FakeReferentielRepository()
    referentiel_repo.seed_hippodrome(Hippodrome(nom="ParisLongchamp", ville="Paris", pays="France"))
    course_repo = FakeCourseRepository(referentiel_repo)
    analyse_repo = FakeAnalyseRepository()
    presse_service = FakeConsensusPresseService()
    utilisateur_repo = FakeUtilisateurRepository()
    audit_repo = FakeAuditRepository()
    statistique_repo = FakeStatistiqueRepository()
    historique_repo = FakeHistoriqueRepository(course_repo, analyse_repo, referentiel_repo)
    journal_repo = FakeJournalRepository()
    tache_repo = FakeTacheRepository()
    parametre_repo = FakeParametreRepository()
    version_repo = FakeVersionRepository()
    collecte_service = FakeCollecteService()
    controle_roi_service = FakeControleRoiService()
    supervision_service = FakeSupervisionService()
    return {
        "referentiel": referentiel_repo,
        "course": course_repo,
        "analyse": analyse_repo,
        "presse": presse_service,
        "utilisateurs": utilisateur_repo,
        "audit": audit_repo,
        "statistiques": statistique_repo,
        "historique": historique_repo,
        "journal": journal_repo,
        "tache": tache_repo,
        "parametre": parametre_repo,
        "version": version_repo,
        "collecte": collecte_service,
        "controle_roi": controle_roi_service,
        "supervision": supervision_service,
    }


@pytest.fixture
def client(repos):
    """Client pour les tests qui ne portent pas sur l'authentification elle-même :
    contourne `get_utilisateur_courant` (utilisateur Administrateur fictif), pour ne
    pas obliger chaque test métier existant à se connecter d'abord."""
    app.dependency_overrides[get_referentiel_repository] = lambda: repos["referentiel"]
    app.dependency_overrides[get_course_repository] = lambda: repos["course"]
    app.dependency_overrides[get_analyse_repository] = lambda: repos["analyse"]
    app.dependency_overrides[get_analyse_service] = lambda: AnalyseService(repos["analyse"])
    app.dependency_overrides[get_preparation_service] = lambda: PreparationDonneesService(
        repos["course"], repos["statistiques"], repos["presse"]
    )
    app.dependency_overrides[get_statistique_repository] = lambda: repos["statistiques"]
    app.dependency_overrides[get_audit_repository] = lambda: repos["audit"]
    app.dependency_overrides[get_historique_repository] = lambda: repos["historique"]
    app.dependency_overrides[get_journal_repository] = lambda: repos["journal"]
    app.dependency_overrides[get_tache_repository] = lambda: repos["tache"]
    app.dependency_overrides[get_parametre_repository] = lambda: repos["parametre"]
    app.dependency_overrides[get_version_repository] = lambda: repos["version"]
    app.dependency_overrides[get_collecte_service] = lambda: repos["collecte"]
    app.dependency_overrides[get_controle_roi_service] = lambda: repos["controle_roi"]
    app.dependency_overrides[get_supervision_service] = lambda: repos["supervision"]
    app.dependency_overrides[get_automatisation_service] = lambda: AutomatisationService(
        repos["course"],
        PreparationDonneesService(repos["course"], repos["statistiques"], repos["presse"]),
        AnalyseService(repos["analyse"]),
    )
    app.dependency_overrides[get_statistique_service] = lambda: StatistiqueService(repos["statistiques"])
    role_admin = Role(id=1, nom="Administrateur")
    utilisateur_test = Utilisateur(id=1, login="test", mot_de_passe="", role_id=1)
    app.dependency_overrides[get_utilisateur_courant] = lambda: (utilisateur_test, role_admin)

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def client_auth_reelle(repos):
    """Client pour les tests d'authentification eux-mêmes : la dépendance
    `get_utilisateur_courant` n'est PAS contournée, seul `get_auth_service` (et les
    repositories des routes utilisées comme cible, ex. /hippodromes) sont câblés sur
    des repositories en mémoire (pas de base réelle)."""
    app.dependency_overrides[get_auth_service] = lambda: AuthService(
        repos["utilisateurs"], repos["audit"], duree_session_minutes=60
    )
    app.dependency_overrides[get_referentiel_repository] = lambda: repos["referentiel"]

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
