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
from src.repositories.historique_repository import HistoriqueRepository
from src.repositories.journal_repository import JournalRepository
from src.repositories.parametre_repository import ParametreRepository
from src.repositories.referentiel_repository import ReferentielRepository
from src.repositories.statistique_repository import StatistiqueRepository
from src.repositories.tache_repository import TacheRepository
from src.repositories.utilisateur_repository import UtilisateurRepository
from src.repositories.version_repository import VersionRepository


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


def get_historique_repository(conn: psycopg.Connection = Depends(get_connection)) -> HistoriqueRepository:
    return HistoriqueRepository(conn)


def get_journal_repository(conn: psycopg.Connection = Depends(get_connection)) -> JournalRepository:
    return JournalRepository(conn)


def get_tache_repository(conn: psycopg.Connection = Depends(get_connection)) -> TacheRepository:
    return TacheRepository(conn)


def get_parametre_repository(conn: psycopg.Connection = Depends(get_connection)) -> ParametreRepository:
    return ParametreRepository(conn)


def get_version_repository(conn: psycopg.Connection = Depends(get_connection)) -> VersionRepository:
    return VersionRepository(conn)
