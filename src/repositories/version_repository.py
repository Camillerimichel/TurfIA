"""Repository de la table `version` — cf. L018 §10 (« consulter les versions »).

Peuplée hors API par `scripts/publier_version.py` (geste de déploiement, pas
une action d'exploitation quotidienne) ; consultée en lecture par
l'Administration.
"""

from __future__ import annotations

import psycopg
from psycopg.rows import class_row

from src.models.technique import Version


class VersionRepository:
    def __init__(self, conn: psycopg.Connection) -> None:
        self._conn = conn

    def creer(self, version: Version) -> Version:
        with self._conn.cursor(row_factory=class_row(Version)) as cur:
            cur.execute(
                """
                INSERT INTO version (version, commit_git, branche, commentaire)
                VALUES (%s, %s, %s, %s)
                RETURNING id, version, commit_git, branche, date_publication, commentaire
                """,
                (version.version, version.commit_git, version.branche, version.commentaire),
            )
            return cur.fetchone()

    def lister(self, limite: int = 20) -> list[Version]:
        with self._conn.cursor(row_factory=class_row(Version)) as cur:
            cur.execute(
                """
                SELECT id, version, commit_git, branche, date_publication, commentaire
                FROM version ORDER BY date_publication DESC LIMIT %s
                """,
                (limite,),
            )
            return cur.fetchall()
