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
        # `debut` fixé explicitement via `clock_timestamp()` plutôt que de
        # laisser le défaut de colonne (`now()`) s'en charger : `now()` est figé
        # à l'heure de début de la transaction PostgreSQL (cf. `terminer`
        # ci-dessous), pas à l'instant réel de cette requête.
        with self._conn.cursor(row_factory=class_row(Tache)) as cur:
            cur.execute(
                """
                INSERT INTO tache (nom, categorie, statut, debut)
                VALUES (%s, %s, 'en_cours', clock_timestamp())
                RETURNING id, nom, categorie, debut, fin, duree_ms, statut, commentaire
                """,
                (nom, categorie),
            )
            return cur.fetchone()

    def terminer(self, tache_id: int, statut: str, commentaire: str | None = None) -> Tache | None:
        # `clock_timestamp()`, jamais `now()` : `now()` (= `CURRENT_TIMESTAMP`)
        # renvoie la même valeur du début à la fin d'une transaction — avec une
        # seule connexion par requête (cf. `get_connection`), `demarrer` et
        # `terminer` s'exécutent dans la même transaction, donc `fin - debut`
        # calculé avec `now()` valait toujours 0 quel que soit le travail réel
        # effectué entre les deux appels. `clock_timestamp()` reflète l'heure
        # réelle de chaque instruction, y compris à l'intérieur d'une même
        # transaction.
        with self._conn.cursor(row_factory=class_row(Tache)) as cur:
            cur.execute(
                """
                UPDATE tache
                SET fin = clock_timestamp(),
                    duree_ms = ROUND(EXTRACT(EPOCH FROM (clock_timestamp() - debut)) * 1000)::int,
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

    def get_derniere_par_nom(self, nom: str) -> Tache | None:
        """Dernière exécution (peu importe le statut) d'une tâche par son nom
        — cf. GET /administration/cron (tableau de bord des tâches
        quotidiennes, une ligne par nom de tâche connu)."""
        with self._conn.cursor(row_factory=class_row(Tache)) as cur:
            cur.execute(
                """
                SELECT id, nom, categorie, debut, fin, duree_ms, statut, commentaire
                FROM tache WHERE nom = %s ORDER BY debut DESC LIMIT 1
                """,
                (nom,),
            )
            return cur.fetchone()

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
