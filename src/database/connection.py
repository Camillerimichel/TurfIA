"""Gestion des connexions et des sessions SQL — cf. L015 §4.

Expose les sessions sous forme de gestionnaire de contexte : une session est toujours
fermée (commit ou rollback explicite) même en cas d'exception (cf. L015 §4.2). Aucun
autre module n'ouvre de connexion directement (cf. L015 §4.1).
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import psycopg

from src.core.config import Settings, get_settings
from src.core.exceptions import DatabaseError


@contextmanager
def session(settings: Settings | None = None) -> Iterator[psycopg.Connection]:
    """Fournit une connexion avec commit automatique en sortie normale, rollback sinon.

    Usage :
        with session() as conn:
            with conn.cursor() as cur:
                cur.execute(...)
    """
    settings = settings or get_settings()
    try:
        conn = psycopg.connect(settings.database_url)
    except psycopg.OperationalError as exc:
        raise DatabaseError(f"Connexion à la base de données impossible : {exc}") from exc

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
