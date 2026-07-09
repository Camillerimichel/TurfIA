"""Repository de la table `parametre` — cf. L011 §10.4, L026 §3.3, L018 §10.

Catalogue fixe de clés (semées par migration) : GET/PATCH seulement, pas de
POST/DELETE (cf. plan Historique/Administration, hypothèse assumée).
"""

from __future__ import annotations

import psycopg
from psycopg.rows import class_row

from src.models.technique import Parametre


class ParametreRepository:
    def __init__(self, conn: psycopg.Connection) -> None:
        self._conn = conn

    def lister(self) -> list[Parametre]:
        with self._conn.cursor(row_factory=class_row(Parametre)) as cur:
            cur.execute(
                "SELECT id, cle, valeur, type, description, date_modification FROM parametre ORDER BY cle"
            )
            return cur.fetchall()

    def get_parametre(self, cle: str) -> Parametre | None:
        with self._conn.cursor(row_factory=class_row(Parametre)) as cur:
            cur.execute(
                "SELECT id, cle, valeur, type, description, date_modification FROM parametre WHERE cle = %s",
                (cle,),
            )
            return cur.fetchone()

    def update_parametre(self, cle: str, valeur: str) -> Parametre | None:
        with self._conn.cursor(row_factory=class_row(Parametre)) as cur:
            cur.execute(
                """
                UPDATE parametre SET valeur = %s, date_modification = now()
                WHERE cle = %s
                RETURNING id, cle, valeur, type, description, date_modification
                """,
                (valeur, cle),
            )
            return cur.fetchone()

    def obtenir_poids(self, prefixe: str) -> dict[str, float]:
        """`{suffixe: valeur}` pour toutes les clés `prefixe.*` — cf.
        `AnalyseService`/`calculer_score`/`calculer_risque` (poids par sous-score/
        sous-risque). Dictionnaire vide si la table est vide ou le préfixe absent :
        l'appelant retombe alors sur `PONDERATIONS_PAR_DEFAUT` (cf. `poids or ...`)."""
        with self._conn.cursor() as cur:
            cur.execute("SELECT cle, valeur FROM parametre WHERE cle LIKE %s", (f"{prefixe}.%",))
            return {cle.removeprefix(f"{prefixe}."): float(valeur) for cle, valeur in cur.fetchall()}
