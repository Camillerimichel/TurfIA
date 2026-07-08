"""Dépendances FastAPI d'accès aux données — cf. L015 §4, §6.

L'API n'accède jamais directement à la base : elle passe par une session puis un
repository (cf. ADR-004 de L001).
"""

from __future__ import annotations

from collections.abc import Generator

import psycopg
from fastapi import Depends

from src.database.connection import session as db_session
from src.repositories.analyse_repository import AnalyseRepository
from src.repositories.audit_repository import AuditRepository
from src.repositories.course_repository import CourseRepository
from src.repositories.referentiel_repository import ReferentielRepository
from src.repositories.statistique_repository import StatistiqueRepository
from src.repositories.utilisateur_repository import UtilisateurRepository


def get_connection() -> Generator[psycopg.Connection, None, None]:
    with db_session() as conn:
        yield conn


def get_referentiel_repository(conn: psycopg.Connection = Depends(get_connection)) -> ReferentielRepository:
    return ReferentielRepository(conn)


def get_course_repository(conn: psycopg.Connection = Depends(get_connection)) -> CourseRepository:
    return CourseRepository(conn)


def get_analyse_repository(conn: psycopg.Connection = Depends(get_connection)) -> AnalyseRepository:
    return AnalyseRepository(conn)


def get_utilisateur_repository(conn: psycopg.Connection = Depends(get_connection)) -> UtilisateurRepository:
    return UtilisateurRepository(conn)


def get_audit_repository(conn: psycopg.Connection = Depends(get_connection)) -> AuditRepository:
    return AuditRepository(conn)


def get_statistique_repository(conn: psycopg.Connection = Depends(get_connection)) -> StatistiqueRepository:
    return StatistiqueRepository(conn)
