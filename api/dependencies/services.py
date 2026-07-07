"""Dépendances FastAPI vers les services applicatifs — cf. L015 §7."""

from __future__ import annotations

from fastapi import Depends

from api.dependencies.db import get_analyse_repository, get_course_repository
from src.repositories.analyse_repository import AnalyseRepository
from src.repositories.course_repository import CourseRepository
from src.services.analyse_service import AnalyseService
from src.services.preparation_service import PreparationDonneesService


def get_analyse_service(repo: AnalyseRepository = Depends(get_analyse_repository)) -> AnalyseService:
    return AnalyseService(repo)


def get_preparation_service(repo: CourseRepository = Depends(get_course_repository)) -> PreparationDonneesService:
    return PreparationDonneesService(repo)
