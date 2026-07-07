"""Repository des tables de référence — cf. L015 §6, L030.1.

Encapsule toutes les requêtes SQL sur les référentiels ; aucun autre module ne doit
écrire de SQL directement sur ces tables (cf. L015 §4.1, L021 §7.2 requêtes paramétrées).
"""

from __future__ import annotations

import psycopg
from psycopg.rows import class_row

from src.models.referentiels import Discipline, EtatPiste, Hippodrome, Surface, TypeCourse


class ReferentielRepository:
    def __init__(self, conn: psycopg.Connection) -> None:
        self._conn = conn

    def list_hippodromes(self) -> list[Hippodrome]:
        with self._conn.cursor(row_factory=class_row(Hippodrome)) as cur:
            cur.execute(
                """
                SELECT id, nom, ville, pays, corde_id, altitude, latitude, longitude, cree_le
                FROM hippodrome
                ORDER BY nom
                """
            )
            return cur.fetchall()

    def get_hippodrome(self, hippodrome_id: int) -> Hippodrome | None:
        with self._conn.cursor(row_factory=class_row(Hippodrome)) as cur:
            cur.execute(
                """
                SELECT id, nom, ville, pays, corde_id, altitude, latitude, longitude, cree_le
                FROM hippodrome
                WHERE id = %s
                """,
                (hippodrome_id,),
            )
            return cur.fetchone()

    def list_disciplines(self) -> list[Discipline]:
        with self._conn.cursor(row_factory=class_row(Discipline)) as cur:
            cur.execute("SELECT id, libelle, description FROM discipline ORDER BY libelle")
            return cur.fetchall()

    def list_surfaces(self) -> list[Surface]:
        with self._conn.cursor(row_factory=class_row(Surface)) as cur:
            cur.execute("SELECT id, libelle, description FROM surface ORDER BY libelle")
            return cur.fetchall()

    def list_etats_piste(self) -> list[EtatPiste]:
        with self._conn.cursor(row_factory=class_row(EtatPiste)) as cur:
            cur.execute("SELECT id, libelle, indice FROM etat_piste ORDER BY indice")
            return cur.fetchall()

    def list_types_course(self) -> list[TypeCourse]:
        with self._conn.cursor(row_factory=class_row(TypeCourse)) as cur:
            cur.execute("SELECT id, libelle, description FROM type_course ORDER BY libelle")
            return cur.fetchall()
