"""Repository des tables de référence — cf. L015 §6, L030.1.

Encapsule toutes les requêtes SQL sur les référentiels ; aucun autre module ne doit
écrire de SQL directement sur ces tables (cf. L015 §4.1, L021 §7.2 requêtes paramétrées).
"""

from __future__ import annotations

import psycopg
from psycopg.rows import class_row

from src.models.referentiels import Discipline, Distance, EtatPiste, Hippodrome, Surface, TypeCourse


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

    def get_discipline(self, discipline_id: int) -> Discipline | None:
        with self._conn.cursor(row_factory=class_row(Discipline)) as cur:
            cur.execute("SELECT id, libelle, description FROM discipline WHERE id = %s", (discipline_id,))
            return cur.fetchone()

    def list_surfaces(self) -> list[Surface]:
        with self._conn.cursor(row_factory=class_row(Surface)) as cur:
            cur.execute("SELECT id, libelle, description FROM surface ORDER BY libelle")
            return cur.fetchall()

    def get_surface(self, surface_id: int) -> Surface | None:
        with self._conn.cursor(row_factory=class_row(Surface)) as cur:
            cur.execute("SELECT id, libelle, description FROM surface WHERE id = %s", (surface_id,))
            return cur.fetchone()

    def list_etats_piste(self) -> list[EtatPiste]:
        with self._conn.cursor(row_factory=class_row(EtatPiste)) as cur:
            cur.execute("SELECT id, libelle, indice FROM etat_piste ORDER BY indice")
            return cur.fetchall()

    def get_etat_piste(self, etat_piste_id: int) -> EtatPiste | None:
        with self._conn.cursor(row_factory=class_row(EtatPiste)) as cur:
            cur.execute("SELECT id, libelle, indice FROM etat_piste WHERE id = %s", (etat_piste_id,))
            return cur.fetchone()

    def list_types_course(self) -> list[TypeCourse]:
        with self._conn.cursor(row_factory=class_row(TypeCourse)) as cur:
            cur.execute("SELECT id, libelle, description FROM type_course ORDER BY libelle")
            return cur.fetchall()

    def get_type_course(self, type_course_id: int) -> TypeCourse | None:
        with self._conn.cursor(row_factory=class_row(TypeCourse)) as cur:
            cur.execute("SELECT id, libelle, description FROM type_course WHERE id = %s", (type_course_id,))
            return cur.fetchone()

    def get_distance(self, distance_id: int) -> Distance | None:
        with self._conn.cursor(row_factory=class_row(Distance)) as cur:
            cur.execute("SELECT id, distance, unite FROM distance WHERE id = %s", (distance_id,))
            return cur.fetchone()

    # -- get-or-create : cf. L013 §3.3 (idempotence), utilisées par la collecte -----

    def get_or_create_hippodrome(self, nom: str, ville: str | None = None, pays: str | None = None) -> Hippodrome:
        with self._conn.cursor(row_factory=class_row(Hippodrome)) as cur:
            cur.execute(
                """
                INSERT INTO hippodrome (nom, ville, pays) VALUES (%s, %s, %s)
                ON CONFLICT (nom) DO NOTHING
                RETURNING id, nom, ville, pays, corde_id, altitude, latitude, longitude, cree_le
                """,
                (nom, ville, pays),
            )
            ligne = cur.fetchone()
        return ligne if ligne is not None else self._get_hippodrome_par_nom(nom)

    def _get_hippodrome_par_nom(self, nom: str) -> Hippodrome:
        with self._conn.cursor(row_factory=class_row(Hippodrome)) as cur:
            cur.execute(
                "SELECT id, nom, ville, pays, corde_id, altitude, latitude, longitude, cree_le "
                "FROM hippodrome WHERE nom = %s",
                (nom,),
            )
            return cur.fetchone()

    def get_or_create_discipline(self, libelle: str) -> Discipline:
        with self._conn.cursor(row_factory=class_row(Discipline)) as cur:
            cur.execute(
                """
                INSERT INTO discipline (libelle) VALUES (%s)
                ON CONFLICT (libelle) DO NOTHING
                RETURNING id, libelle, description
                """,
                (libelle,),
            )
            ligne = cur.fetchone()
            if ligne is not None:
                return ligne
            cur.execute("SELECT id, libelle, description FROM discipline WHERE libelle = %s", (libelle,))
            return cur.fetchone()

    def get_or_create_surface(self, libelle: str) -> Surface:
        with self._conn.cursor(row_factory=class_row(Surface)) as cur:
            cur.execute(
                """
                INSERT INTO surface (libelle) VALUES (%s)
                ON CONFLICT (libelle) DO NOTHING
                RETURNING id, libelle, description
                """,
                (libelle,),
            )
            ligne = cur.fetchone()
            if ligne is not None:
                return ligne
            cur.execute("SELECT id, libelle, description FROM surface WHERE libelle = %s", (libelle,))
            return cur.fetchone()

    def get_or_create_etat_piste(self, libelle: str) -> EtatPiste:
        with self._conn.cursor(row_factory=class_row(EtatPiste)) as cur:
            cur.execute(
                """
                INSERT INTO etat_piste (libelle) VALUES (%s)
                ON CONFLICT (libelle) DO NOTHING
                RETURNING id, libelle, indice
                """,
                (libelle,),
            )
            ligne = cur.fetchone()
            if ligne is not None:
                return ligne
            cur.execute("SELECT id, libelle, indice FROM etat_piste WHERE libelle = %s", (libelle,))
            return cur.fetchone()

    def get_or_create_distance(self, distance: int, unite: str = "m") -> Distance:
        with self._conn.cursor(row_factory=class_row(Distance)) as cur:
            cur.execute(
                """
                INSERT INTO distance (distance, unite) VALUES (%s, %s)
                ON CONFLICT (distance, unite) DO NOTHING
                RETURNING id, distance, unite
                """,
                (distance, unite),
            )
            ligne = cur.fetchone()
            if ligne is not None:
                return ligne
            cur.execute("SELECT id, distance, unite FROM distance WHERE distance = %s AND unite = %s", (distance, unite))
            return cur.fetchone()
