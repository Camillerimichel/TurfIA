import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "postgresql://dummy@localhost/dummy")
os.environ.setdefault("SECRET_KEY", "dummy")

from api.dependencies.db import get_analyse_repository, get_course_repository, get_referentiel_repository  # noqa: E402
from api.dependencies.services import get_analyse_service  # noqa: E402
from api.main import app  # noqa: E402
from src.models.referentiels import Hippodrome  # noqa: E402
from src.services.analyse_service import AnalyseService  # noqa: E402
from tests.integration.fakes import FakeAnalyseRepository, FakeCourseRepository, FakeReferentielRepository  # noqa: E402


@pytest.fixture
def repos():
    referentiel_repo = FakeReferentielRepository()
    referentiel_repo.seed_hippodrome(Hippodrome(nom="ParisLongchamp", ville="Paris", pays="France"))
    course_repo = FakeCourseRepository()
    analyse_repo = FakeAnalyseRepository()
    return {"referentiel": referentiel_repo, "course": course_repo, "analyse": analyse_repo}


@pytest.fixture
def client(repos):
    app.dependency_overrides[get_referentiel_repository] = lambda: repos["referentiel"]
    app.dependency_overrides[get_course_repository] = lambda: repos["course"]
    app.dependency_overrides[get_analyse_repository] = lambda: repos["analyse"]
    app.dependency_overrides[get_analyse_service] = lambda: AnalyseService(repos["analyse"])

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
