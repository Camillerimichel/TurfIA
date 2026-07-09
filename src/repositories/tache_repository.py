"""Repository de la table `tache` — cf. L017 §5, L018 §10.

Trace l'exécution des automatisations déclenchées manuellement depuis le
module Administration (collecte, analyse du jour, statistiques, sauvegarde).
"""

from __future__ import annotations

from datetime import datetime

import psycopg
from psycopg.rows import class_row

from src.models.technique import Tache


class TacheRepository:
    def __init__(self, conn: psycopg.Connection) -> None:
        self._conn = conn

    def demarrer(self, nom: str, categorie: str | None = None) -> Tache:
        with self._conn.cursor(row_factory=class_row(Tache)) as cur:
            cur.execute(
                """
                INSERT INTO tache (nom, categorie, statut)
                VALUES (%s, %s, 'en_cours')
                RETURNING id, nom, categorie, debut, fin, duree_ms, statut, commentaire
                """,
                (nom, categorie),
            )
            return cur.fetchone()

    def terminer(self, tache_id: int, statut: str, commentaire: str | None = None) -> Tache | None:
        with self._conn.cursor(row_factory=class_row(Tache)) as cur:
            cur.execute(
                """
                UPDATE tache
                SET fin = now(),
                    duree_ms = ROUND(EXTRACT(EPOCH FROM (now() - debut)) * 1000)::int,
                    statut = %s,
                    commentaire = %s
                WHERE id = %s
                RETURNING id, nom, categorie, debut, fin, duree_ms, statut, commentaire
                """,
                (statut, commentaire, tache_id),
            )
            return cur.fetchone()

    def lister(self, categorie: str | None = None, limite: int = 50) -> list[Tache]:
        with self._conn.cursor(row_factory=class_row(Tache)) as cur:
            if categorie is not None:
                cur.execute(
                    """
                    SELECT id, nom, categorie, debut, fin, duree_ms, statut, commentaire
                    FROM tache WHERE categorie = %s ORDER BY debut DESC LIMIT %s
                    """,
                    (categorie, limite),
                )
            else:
                cur.execute(
                    """
                    SELECT id, nom, categorie, debut, fin, duree_ms, statut, commentaire
                    FROM tache ORDER BY debut DESC LIMIT %s
                    """,
                    (limite,),
                )
            return cur.fetchall()

    def compter_echecs_recents(self, depuis: datetime, categorie: str | None = None) -> int:
        with self._conn.cursor() as cur:
            if categorie is not None:
                cur.execute(
                    "SELECT COUNT(*) FROM tache WHERE statut = 'echec' AND debut >= %s AND categorie = %s",
                    (depuis, categorie),
                )
            else:
                cur.execute("SELECT COUNT(*) FROM tache WHERE statut = 'echec' AND debut >= %s", (depuis,))
            return cur.fetchone()[0]
