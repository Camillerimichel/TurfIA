"""Dépendances FastAPI vers les services applicatifs — cf. L015 §7."""

from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends

from api.dependencies.db import get_analyse_repository, get_course_repository
from src.collecte.canalturf.client import CanalturfClient
from src.repositories.analyse_repository import AnalyseRepository
from src.repositories.course_repository import CourseRepository
from src.services.analyse_service import AnalyseService
from src.services.consensus_presse_service import ConsensusPresseService
from src.services.preparation_service import PreparationDonneesService


def get_analyse_service(repo: AnalyseRepository = Depends(get_analyse_repository)) -> AnalyseService:
    return AnalyseService(repo)


def get_consensus_presse_service() -> Generator[ConsensusPresseService, None, None]:
    with CanalturfClient() as client:
        yield ConsensusPresseService(client)


def get_preparation_service(
    repo: CourseRepository = Depends(get_course_repository),
    presse: ConsensusPresseService = Depends(get_consensus_presse_service),
) -> PreparationDonneesService:
    return PreparationDonneesService(repo, presse)
