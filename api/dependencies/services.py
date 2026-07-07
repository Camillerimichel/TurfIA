"""Dépendances FastAPI vers les services applicatifs — cf. L015 §7."""

from __future__ import annotations

from fastapi import Depends

from api.dependencies.db import get_analyse_repository
from src.repositories.analyse_repository import AnalyseRepository
from src.services.analyse_service import AnalyseService


def get_analyse_service(repo: AnalyseRepository = Depends(get_analyse_repository)) -> AnalyseService:
    return AnalyseService(repo)
