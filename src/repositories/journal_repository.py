"""Repository de la table `journal` — cf. L022, L018 §10.1.

Alimentée par `src/core/log_db_handler.py::DbLogHandler` (WARNING+ uniquement),
consultée en lecture par le module Administration.
"""

from __future__ import annotations

from datetime import date

import psycopg
from psycopg.rows import class_row

from src.models.technique import Journal


class JournalRepository:
    def __init__(self, conn: psycopg.Connection) -> None:
        self._conn = conn

    def enregistrer(
        self,
        niveau: str,
        message: str,
        composant: str | None = None,
        correlation_id: str | None = None,
        exception: str | None = None,
    ) -> Journal:
        with self._conn.cursor(row_factory=class_row(Journal)) as cur:
            cur.execute(
                """
                INSERT INTO journal (niveau, composant, correlation_id, message, exception)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, date_evenement, niveau, composant, correlation_id, message, exception
                """,
                (niveau, composant, correlation_id, message, exception),
            )
            return cur.fetchone()

    def lister(
        self,
        niveau: str | None = None,
        composant: str | None = None,
        date_debut: date | None = None,
        date_fin: date | None = None,
        limite: int = 200,
    ) -> list[Journal]:
        conditions = []
        valeurs: list[object] = []
        if niveau is not None:
            conditions.append("niveau = %s")
            valeurs.append(niveau)
        if composant is not None:
            conditions.append("composant = %s")
            valeurs.append(composant)
        if date_debut is not None:
            conditions.append("date_evenement >= %s")
            valeurs.append(date_debut)
        if date_fin is not None:
            conditions.append("date_evenement <= %s")
            valeurs.append(date_fin)

        clause_where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        valeurs.append(limite)

        with self._conn.cursor(row_factory=class_row(Journal)) as cur:
            cur.execute(
                f"""
                SELECT id, date_evenement, niveau, composant, correlation_id, message, exception
                FROM journal
                {clause_where}
                ORDER BY date_evenement DESC
                LIMIT %s
                """,
                valeurs,
            )
            return cur.fetchall()
