"""Repository de la table `audit` — cf. L021 §8.1, §13, L030.5.

Dans cette tranche, limité aux événements d'authentification (connexion, échec de
connexion, déconnexion) — un audit systématique de chaque écriture sur chaque
ressource est une suite possible, non construite ici (cf. PROJECT_STATE.md).
"""

from __future__ import annotations

import psycopg


class AuditRepository:
    def __init__(self, conn: psycopg.Connection) -> None:
        self._conn = conn

    def enregistrer(self, utilisateur_id: int | None, action: str, objet: str | None = None) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                "INSERT INTO audit (utilisateur_id, action, objet) VALUES (%s, %s, %s)",
                (utilisateur_id, action, objet),
            )
