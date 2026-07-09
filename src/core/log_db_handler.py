"""Handler de logging qui persiste les évènements WARNING+ dans `journal` —
cf. L022, L018 §10 (module Administration, « consulter les journaux »).

`src/core/logging.py` reste la seule source pour stdout (JSON, tous niveaux) ;
ce handler s'ajoute en complément, ne remplace rien.
"""

from __future__ import annotations

import logging

import psycopg


class DbLogHandler(logging.Handler):
    """Connexion dédiée, courte et jetable à chaque évènement — jamais la
    connexion d'une requête en cours (ce handler peut être invoqué en dehors de
    tout contexte de requête, ex. scripts CLI). `connect_timeout` court : une
    panne DB ne doit jamais transformer un log en attente longue. N'appelle
    jamais `logging.*` en cas d'échec (seulement `self.handleError`, qui écrit
    sur stderr par construction stdlib) pour éviter toute récursion.
    """

    def __init__(self, database_url: str, niveau: str = "WARNING") -> None:
        super().__init__(level=getattr(logging, niveau))
        self._database_url = database_url

    def emit(self, record: logging.LogRecord) -> None:
        if record.name.startswith("psycopg"):
            return  # jamais journaliser les logs du driver lui-même -> anti-réentrance
        try:
            with psycopg.connect(self._database_url, connect_timeout=2) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO journal (niveau, composant, correlation_id, message, exception)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            record.levelname,
                            record.name,
                            getattr(record, "correlation_id", None),
                            record.getMessage(),
                            self.formatException(record.exc_info) if record.exc_info else None,
                        ),
                    )
        except Exception:
            self.handleError(record)
