import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "postgresql://dummy@localhost/dummy")
os.environ.setdefault("SECRET_KEY", "dummy")

from api.dependencies.db import get_analyse_repository, get_course_repository, get_referentiel_repository  # noqa: E402
from api.dependencies.services import get_analyse_service, get_preparation_service  # noqa: E402
from api.main import app  # noqa: E402
from src.models.referentiels import Hippodrome  # noqa: E402
from src.services.analyse_service import AnalyseService  # noqa: E402
from src.services.preparation_service import PreparationDonneesService  # noqa: E402
from tests.integration.fakes import (  # noqa: E402
    FakeAnalyseRepository,
    FakeConsensusPresseService,
    FakeCourseRepository,
    FakeReferentielRepository,
)


@pytest.fixture
def repos():
    referentiel_repo = FakeReferentielRepository()
    referentiel_repo.seed_hippodrome(Hippodrome(nom="ParisLongchamp", ville="Paris", pays="France"))
    course_repo = FakeCourseRepository()
    analyse_repo = FakeAnalyseRepository()
    presse_service = FakeConsensusPresseService()
    return {"referentiel": referentiel_repo, "course": course_repo, "analyse": analyse_repo, "presse": presse_service}


@pytest.fixture
def client(repos):
    app.dependency_overrides[get_referentiel_repository] = lambda: repos["referentiel"]
    app.dependency_overrides[get_course_repository] = lambda: repos["course"]
    app.dependency_overrides[get_analyse_repository] = lambda: repos["analyse"]
    app.dependency_overrides[get_analyse_service] = lambda: AnalyseService(repos["analyse"])
    app.dependency_overrides[get_preparation_service] = lambda: PreparationDonneesService(
        repos["course"], repos["presse"]
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
