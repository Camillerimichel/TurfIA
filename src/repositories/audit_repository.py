"""Repository de la table `audit` — cf. L021 §8.1, §13, L030.5.

Couvre les événements d'authentification (connexion, échec de connexion,
déconnexion, cf. `AuthService`) et, depuis le 2026-07-08, chaque écriture sur
une ressource métier via l'API authentifiée (cf. `api/routes/courses.py`,
`api/routes/analyses.py`) — les écritures des traitements planifiés
(hors requête API, sans utilisateur à attribuer) restent hors périmètre,
couvertes uniquement par la journalisation structurée (cf. PROJECT_STATE.md).
"""

from __future__ import annotations

import psycopg
from psycopg.rows import class_row

from src.models.audit import Audit


class AuditRepository:
    def __init__(self, conn: psycopg.Connection) -> None:
        self._conn = conn

    def enregistrer(
        self,
        utilisateur_id: int | None,
        action: str,
        objet: str | None = None,
        ancien_etat: str | None = None,
        nouvel_etat: str | None = None,
    ) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO audit (utilisateur_id, action, objet, ancien_etat, nouvel_etat)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (utilisateur_id, action, objet, ancien_etat, nouvel_etat),
            )

    def lister(self, limite: int = 200) -> list[Audit]:
        with self._conn.cursor(row_factory=class_row(Audit)) as cur:
            cur.execute(
                """
                SELECT id, utilisateur_id, date_action, action, objet, ancien_etat, nouvel_etat
                FROM audit ORDER BY date_action DESC LIMIT %s
                """,
                (limite,),
            )
            return cur.fetchall()
