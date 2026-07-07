"""Repository des tables métier (réunion, course, partant) — cf. L015 §6, L030.2."""

from __future__ import annotations

import psycopg
from psycopg.rows import class_row

from src.models.course import Cheval, Course, Entraineur, Jockey, Partant, Reunion


class CourseRepository:
    def __init__(self, conn: psycopg.Connection) -> None:
        self._conn = conn

    def create_reunion(self, reunion: Reunion) -> Reunion:
        with self._conn.cursor(row_factory=class_row(Reunion)) as cur:
            cur.execute(
                """
                INSERT INTO reunion (date, hippodrome_id, numero, heure_debut, heure_fin, statut)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, date, hippodrome_id, numero, heure_debut, heure_fin, statut
                """,
                (
                    reunion.date,
                    reunion.hippodrome_id,
                    reunion.numero,
                    reunion.heure_debut,
                    reunion.heure_fin,
                    reunion.statut,
                ),
            )
            return cur.fetchone()

    def get_reunion(self, reunion_id: int) -> Reunion | None:
        with self._conn.cursor(row_factory=class_row(Reunion)) as cur:
            cur.execute(
                """
                SELECT id, date, hippodrome_id, numero, heure_debut, heure_fin, statut
                FROM reunion WHERE id = %s
                """,
                (reunion_id,),
            )
            return cur.fetchone()

    def create_course(self, course: Course) -> Course:
        with self._conn.cursor(row_factory=class_row(Course)) as cur:
            cur.execute(
                """
                INSERT INTO course (
                    reunion_id, numero, nom, heure_depart, discipline_id, type_course_id,
                    distance_id, surface_id, etat_piste_id, allocation, nb_partants, quinte
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, reunion_id, numero, nom, heure_depart, discipline_id,
                          type_course_id, distance_id, surface_id, etat_piste_id,
                          allocation, nb_partants, quinte
                """,
                (
                    course.reunion_id,
                    course.numero,
                    course.nom,
                    course.heure_depart,
                    course.discipline_id,
                    course.type_course_id,
                    course.distance_id,
                    course.surface_id,
                    course.etat_piste_id,
                    course.allocation,
                    course.nb_partants,
                    course.quinte,
                ),
            )
            return cur.fetchone()

    def get_course(self, course_id: int) -> Course | None:
        with self._conn.cursor(row_factory=class_row(Course)) as cur:
            cur.execute(
                """
                SELECT id, reunion_id, numero, nom, heure_depart, discipline_id,
                       type_course_id, distance_id, surface_id, etat_piste_id,
                       allocation, nb_partants, quinte
                FROM course WHERE id = %s
                """,
                (course_id,),
            )
            return cur.fetchone()

    def list_courses_by_reunion(self, reunion_id: int) -> list[Course]:
        with self._conn.cursor(row_factory=class_row(Course)) as cur:
            cur.execute(
                """
                SELECT id, reunion_id, numero, nom, heure_depart, discipline_id,
                       type_course_id, distance_id, surface_id, etat_piste_id,
                       allocation, nb_partants, quinte
                FROM course WHERE reunion_id = %s ORDER BY numero
                """,
                (reunion_id,),
            )
            return cur.fetchall()

    def create_partant(self, partant: Partant) -> Partant:
        with self._conn.cursor(row_factory=class_row(Partant)) as cur:
            cur.execute(
                """
                INSERT INTO partant (
                    course_id, cheval_id, jockey_id, entraineur_id, numero, corde,
                    poids, valeur, age, ferrure, musique, non_partant
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, course_id, cheval_id, jockey_id, entraineur_id, numero,
                          corde, poids, valeur, age, ferrure, musique, non_partant
                """,
                (
                    partant.course_id,
                    partant.cheval_id,
                    partant.jockey_id,
                    partant.entraineur_id,
                    partant.numero,
                    partant.corde,
                    partant.poids,
                    partant.valeur,
                    partant.age,
                    partant.ferrure,
                    partant.musique,
                    partant.non_partant,
                ),
            )
            return cur.fetchone()

    def list_partants_by_course(self, course_id: int) -> list[Partant]:
        with self._conn.cursor(row_factory=class_row(Partant)) as cur:
            cur.execute(
                """
                SELECT id, course_id, cheval_id, jockey_id, entraineur_id, numero,
                       corde, poids, valeur, age, ferrure, musique, non_partant
                FROM partant WHERE course_id = %s ORDER BY numero
                """,
                (course_id,),
            )
            return cur.fetchall()

    def create_cheval(self, cheval: Cheval) -> Cheval:
        with self._conn.cursor(row_factory=class_row(Cheval)) as cur:
            cur.execute(
                """
                INSERT INTO cheval (nom, sexe, date_naissance, pere, mere, gains, musique, actif)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, nom, sexe, date_naissance, pere, mere, gains, musique, actif
                """,
                (
                    cheval.nom,
                    cheval.sexe,
                    cheval.date_naissance,
                    cheval.pere,
                    cheval.mere,
                    cheval.gains,
                    cheval.musique,
                    cheval.actif,
                ),
            )
            return cur.fetchone()

    def get_cheval(self, cheval_id: int) -> Cheval | None:
        with self._conn.cursor(row_factory=class_row(Cheval)) as cur:
            cur.execute(
                """
                SELECT id, nom, sexe, date_naissance, pere, mere, gains, musique, actif
                FROM cheval WHERE id = %s
                """,
                (cheval_id,),
            )
            return cur.fetchone()

    def create_jockey(self, jockey: Jockey) -> Jockey:
        with self._conn.cursor(row_factory=class_row(Jockey)) as cur:
            cur.execute(
                """
                INSERT INTO jockey (nom, prenom, licence, actif)
                VALUES (%s, %s, %s, %s)
                RETURNING id, nom, prenom, licence, actif
                """,
                (jockey.nom, jockey.prenom, jockey.licence, jockey.actif),
            )
            return cur.fetchone()

    def get_jockey(self, jockey_id: int) -> Jockey | None:
        with self._conn.cursor(row_factory=class_row(Jockey)) as cur:
            cur.execute("SELECT id, nom, prenom, licence, actif FROM jockey WHERE id = %s", (jockey_id,))
            return cur.fetchone()

    def create_entraineur(self, entraineur: Entraineur) -> Entraineur:
        with self._conn.cursor(row_factory=class_row(Entraineur)) as cur:
            cur.execute(
                """
                INSERT INTO entraineur (nom, prenom, actif)
                VALUES (%s, %s, %s)
                RETURNING id, nom, prenom, actif
                """,
                (entraineur.nom, entraineur.prenom, entraineur.actif),
            )
            return cur.fetchone()

    def get_entraineur(self, entraineur_id: int) -> Entraineur | None:
        with self._conn.cursor(row_factory=class_row(Entraineur)) as cur:
            cur.execute("SELECT id, nom, prenom, actif FROM entraineur WHERE id = %s", (entraineur_id,))
            return cur.fetchone()
