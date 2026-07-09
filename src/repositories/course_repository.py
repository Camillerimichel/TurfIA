"""Repository des tables métier (réunion, course, partant) — cf. L015 §6, L030.2."""

from __future__ import annotations

from datetime import date

import psycopg
from psycopg.rows import class_row

from src.core.exceptions import BusinessRuleError
from src.models.course import Cheval, Cote, Course, Entraineur, Jockey, Partant, Resultat, Reunion


class CourseRepository:
    def __init__(self, conn: psycopg.Connection) -> None:
        self._conn = conn

    def _mettre_a_jour(self, table: str, colonnes_select: str, modele: type, ressource_id: int, champs: dict):
        """`table` et `colonnes_select` sont toujours des littéraux fournis par le
        code appelant (jamais dérivés d'une entrée utilisateur) ; les clés de
        `champs` viennent d'un schéma Pydantic serveur (`exclude_unset`), jamais
        directement des clés JSON brutes du client — pas d'injection possible.
        Utilisé par les PATCH (cf. api/routes/courses.py), jamais sur les tables
        historisées (résultat, cote, analyse...) qui n'exposent pas cette méthode."""
        if not champs:
            with self._conn.cursor(row_factory=class_row(modele)) as cur:
                cur.execute(f"SELECT {colonnes_select} FROM {table} WHERE id = %s", (ressource_id,))
                return cur.fetchone()
        assignations = ", ".join(f"{cle} = %s" for cle in champs)
        valeurs = [*champs.values(), ressource_id]
        with self._conn.cursor(row_factory=class_row(modele)) as cur:
            cur.execute(
                f"UPDATE {table} SET {assignations}, modifie_le = now() WHERE id = %s RETURNING {colonnes_select}",
                valeurs,
            )
            return cur.fetchone()

    def _supprimer(self, table: str, nom_ressource: str, ressource_id: int) -> bool:
        """Supprime la ligne si elle existe et si rien ne la référence. `table` est
        toujours un littéral fourni par le code appelant. Les contraintes FK `ON
        DELETE RESTRICT` (cf. L011 §9) protègent déjà l'intégrité : plutôt que de
        vérifier nous-mêmes à l'avance (risque de TOCTOU sous concurrence), on
        laisse Postgres refuser et on traduit sa violation de contrainte en
        `BusinessRuleError` (409, cf. api/middlewares/error_handler.py) — jamais un
        500 brut. Retourne False si l'id était inconnu (0 ligne supprimée)."""
        try:
            with self._conn.cursor() as cur:
                cur.execute(f"DELETE FROM {table} WHERE id = %s", (ressource_id,))
                return cur.rowcount > 0
        except psycopg.errors.ForeignKeyViolation as exc:
            raise BusinessRuleError(
                f"Impossible de supprimer {nom_ressource} {ressource_id} : des données y sont rattachées."
            ) from exc

    def delete_reunion(self, reunion_id: int) -> bool:
        return self._supprimer("reunion", "la réunion", reunion_id)

    def delete_course(self, course_id: int) -> bool:
        return self._supprimer("course", "la course", course_id)

    def delete_partant(self, partant_id: int) -> bool:
        return self._supprimer("partant", "le partant", partant_id)

    def delete_cheval(self, cheval_id: int) -> bool:
        return self._supprimer("cheval", "le cheval", cheval_id)

    def delete_jockey(self, jockey_id: int) -> bool:
        return self._supprimer("jockey", "le jockey", jockey_id)

    def delete_entraineur(self, entraineur_id: int) -> bool:
        return self._supprimer("entraineur", "l'entraîneur", entraineur_id)

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

    def list_reunions_by_date(self, jour: date) -> list[Reunion]:
        """Réunions d'une date donnée — point d'entrée de navigation pour
        l'interface HTML (cf. L018 §5, « Quinté du jour »/Accueil) : jusqu'ici
        aucune route ne permettait de lister les réunions sans connaître leur
        id à l'avance."""
        with self._conn.cursor(row_factory=class_row(Reunion)) as cur:
            cur.execute(
                """
                SELECT id, date, hippodrome_id, numero, heure_debut, heure_fin, statut
                FROM reunion WHERE date = %s ORDER BY numero
                """,
                (jour,),
            )
            return cur.fetchall()

    def get_or_create_reunion(self, reunion: Reunion) -> Reunion:
        with self._conn.cursor(row_factory=class_row(Reunion)) as cur:
            cur.execute(
                """
                INSERT INTO reunion (date, hippodrome_id, numero, heure_debut, heure_fin, statut)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (date, hippodrome_id, numero) DO NOTHING
                RETURNING id, date, hippodrome_id, numero, heure_debut, heure_fin, statut
                """,
                (reunion.date, reunion.hippodrome_id, reunion.numero, reunion.heure_debut, reunion.heure_fin, reunion.statut),
            )
            ligne = cur.fetchone()
            if ligne is not None:
                return ligne
            cur.execute(
                """
                SELECT id, date, hippodrome_id, numero, heure_debut, heure_fin, statut
                FROM reunion WHERE date = %s AND hippodrome_id = %s AND numero = %s
                """,
                (reunion.date, reunion.hippodrome_id, reunion.numero),
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

    def get_or_create_course(self, course: Course) -> Course:
        with self._conn.cursor(row_factory=class_row(Course)) as cur:
            cur.execute(
                """
                INSERT INTO course (
                    reunion_id, numero, nom, heure_depart, discipline_id, type_course_id,
                    distance_id, surface_id, etat_piste_id, allocation, nb_partants, quinte
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (reunion_id, numero) DO NOTHING
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
            ligne = cur.fetchone()
            if ligne is not None:
                return ligne
            cur.execute(
                """
                SELECT id, reunion_id, numero, nom, heure_depart, discipline_id,
                       type_course_id, distance_id, surface_id, etat_piste_id,
                       allocation, nb_partants, quinte
                FROM course WHERE reunion_id = %s AND numero = %s
                """,
                (course.reunion_id, course.numero),
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

    def list_courses_avec_resultat(self, date_debut: date, date_fin: date) -> list[Course]:
        """Courses déjà arrivées (résultat officiel connu) dans une fenêtre de
        dates — périmètre du moteur de rejeu (cf. `scripts/rejouer_versions.py`,
        L031.7 §4) : rejouer une course exige de connaître son arrivée réelle."""
        with self._conn.cursor(row_factory=class_row(Course)) as cur:
            cur.execute(
                """
                SELECT c.id, c.reunion_id, c.numero, c.nom, c.heure_depart, c.discipline_id,
                       c.type_course_id, c.distance_id, c.surface_id, c.etat_piste_id,
                       c.allocation, c.nb_partants, c.quinte
                FROM course c
                JOIN reunion re ON re.id = c.reunion_id
                WHERE re.date BETWEEN %s AND %s
                  AND EXISTS (SELECT 1 FROM resultat r WHERE r.course_id = c.id)
                ORDER BY re.date, c.numero
                """,
                (date_debut, date_fin),
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

    def get_or_create_partant(self, partant: Partant) -> Partant:
        with self._conn.cursor(row_factory=class_row(Partant)) as cur:
            cur.execute(
                """
                INSERT INTO partant (
                    course_id, cheval_id, jockey_id, entraineur_id, numero, corde,
                    poids, valeur, age, ferrure, musique, non_partant
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (course_id, numero) DO NOTHING
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
            ligne = cur.fetchone()
            if ligne is not None:
                return ligne
            cur.execute(
                """
                SELECT id, course_id, cheval_id, jockey_id, entraineur_id, numero,
                       corde, poids, valeur, age, ferrure, musique, non_partant
                FROM partant WHERE course_id = %s AND numero = %s
                """,
                (partant.course_id, partant.numero),
            )
            return cur.fetchone()

    def get_partant(self, partant_id: int) -> Partant | None:
        with self._conn.cursor(row_factory=class_row(Partant)) as cur:
            cur.execute(
                """
                SELECT id, course_id, cheval_id, jockey_id, entraineur_id, numero,
                       corde, poids, valeur, age, ferrure, musique, non_partant
                FROM partant WHERE id = %s
                """,
                (partant_id,),
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

    # -- get-or-create par nom : aucune contrainte UNIQUE sur cheval/jockey/entraineur
    # en base (cf. L030.2) -> SELECT puis INSERT si absent, non atomique. Acceptable
    # pour un script de collecte manuel non concurrent (limite documentée dans
    # PROJECT_STATE.md) ; à revoir si la collecte devient concurrente/planifiée.

    def get_or_create_cheval(self, cheval: Cheval) -> Cheval:
        with self._conn.cursor(row_factory=class_row(Cheval)) as cur:
            cur.execute(
                "SELECT id, nom, sexe, date_naissance, pere, mere, gains, musique, actif "
                "FROM cheval WHERE nom = %s",
                (cheval.nom,),
            )
            existant = cur.fetchone()
        return existant if existant is not None else self.create_cheval(cheval)

    def get_or_create_jockey(self, jockey: Jockey) -> Jockey:
        with self._conn.cursor(row_factory=class_row(Jockey)) as cur:
            cur.execute("SELECT id, nom, prenom, licence, actif FROM jockey WHERE nom = %s", (jockey.nom,))
            existant = cur.fetchone()
        return existant if existant is not None else self.create_jockey(jockey)

    def get_or_create_entraineur(self, entraineur: Entraineur) -> Entraineur:
        with self._conn.cursor(row_factory=class_row(Entraineur)) as cur:
            cur.execute("SELECT id, nom, prenom, actif FROM entraineur WHERE nom = %s", (entraineur.nom,))
            existant = cur.fetchone()
        return existant if existant is not None else self.create_entraineur(entraineur)

    def create_cote(self, cote: Cote) -> Cote:
        """Toujours un nouvel enregistrement : une cote n'est jamais remplacée mais
        historisée (cf. L011 §15).
        """
        with self._conn.cursor(row_factory=class_row(Cote)) as cur:
            cur.execute(
                """
                INSERT INTO cote (partant_id, operateur, cote, evolution, date_maj)
                VALUES (%s, %s, %s, %s, COALESCE(%s, now()))
                RETURNING id, partant_id, operateur, cote, evolution, date_maj
                """,
                (cote.partant_id, cote.operateur, cote.cote, cote.evolution, cote.date_maj),
            )
            return cur.fetchone()

    def list_cotes_by_partant(self, partant_id: int) -> list[Cote]:
        with self._conn.cursor(row_factory=class_row(Cote)) as cur:
            cur.execute(
                """
                SELECT id, partant_id, operateur, cote, evolution, date_maj
                FROM cote WHERE partant_id = %s ORDER BY date_maj DESC
                """,
                (partant_id,),
            )
            return cur.fetchall()

    def get_dernieres_cotes_par_course(self, course_id: int) -> dict[int, float]:
        """Dernière cote connue (la plus récente `date_maj`) par partant d'une
        course, cf. L031.2 famille Marché. Un partant sans cote collectée est
        simplement absent du dictionnaire retourné.
        """
        with self._conn.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT ON (co.partant_id) co.partant_id, co.cote
                FROM cote co
                JOIN partant pa ON pa.id = co.partant_id
                WHERE pa.course_id = %s
                ORDER BY co.partant_id, co.date_maj DESC
                """,
                (course_id,),
            )
            return {partant_id: float(cote) for partant_id, cote in cur.fetchall()}

    def get_or_create_resultat(self, resultat: Resultat) -> Resultat:
        with self._conn.cursor(row_factory=class_row(Resultat)) as cur:
            cur.execute(
                """
                INSERT INTO resultat (course_id, partant_id, classement, temps, ecart, disqualification, non_partant)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (course_id, classement) DO NOTHING
                RETURNING id, course_id, partant_id, classement, temps, ecart, disqualification, non_partant
                """,
                (
                    resultat.course_id,
                    resultat.partant_id,
                    resultat.classement,
                    resultat.temps,
                    resultat.ecart,
                    resultat.disqualification,
                    resultat.non_partant,
                ),
            )
            ligne = cur.fetchone()
            if ligne is not None:
                return ligne
            cur.execute(
                """
                SELECT id, course_id, partant_id, classement, temps, ecart, disqualification, non_partant
                FROM resultat WHERE course_id = %s AND classement = %s
                """,
                (resultat.course_id, resultat.classement),
            )
            return cur.fetchone()

    def list_resultats_by_course(self, course_id: int) -> list[Resultat]:
        with self._conn.cursor(row_factory=class_row(Resultat)) as cur:
            cur.execute(
                """
                SELECT id, course_id, partant_id, classement, temps, ecart, disqualification, non_partant
                FROM resultat WHERE course_id = %s ORDER BY classement NULLS LAST
                """,
                (course_id,),
            )
            return cur.fetchall()

    def compter_performances_jockey(self, jockey_id: int, exclure_course_id: int) -> tuple[int, int]:
        """(victoires, courses) du jockey hors course en cours d'analyse — cf.
        L031.2 famille Professionnels."""
        with self._conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) FILTER (WHERE r.classement = 1 AND NOT r.disqualification), COUNT(*)
                FROM partant p
                JOIN resultat r ON r.partant_id = p.id
                WHERE p.jockey_id = %s AND p.course_id != %s AND NOT r.non_partant
                """,
                (jockey_id, exclure_course_id),
            )
            return cur.fetchone()

    def compter_performances_entraineur(self, entraineur_id: int, exclure_course_id: int) -> tuple[int, int]:
        """(victoires, courses) de l'entraîneur hors course en cours d'analyse — cf.
        L031.2 famille Professionnels."""
        with self._conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) FILTER (WHERE r.classement = 1 AND NOT r.disqualification), COUNT(*)
                FROM partant p
                JOIN resultat r ON r.partant_id = p.id
                WHERE p.entraineur_id = %s AND p.course_id != %s AND NOT r.non_partant
                """,
                (entraineur_id, exclure_course_id),
            )
            return cur.fetchone()

    def compter_performances_couple(
        self, jockey_id: int, entraineur_id: int, exclure_course_id: int
    ) -> tuple[int, int]:
        """(victoires, courses) du couple jockey/entraîneur hors course en cours
        d'analyse — cf. L031.2 famille Professionnels."""
        with self._conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) FILTER (WHERE r.classement = 1 AND NOT r.disqualification), COUNT(*)
                FROM partant p
                JOIN resultat r ON r.partant_id = p.id
                WHERE p.jockey_id = %s AND p.entraineur_id = %s AND p.course_id != %s AND NOT r.non_partant
                """,
                (jockey_id, entraineur_id, exclure_course_id),
            )
            return cur.fetchone()

    def compter_performances_cheval_hippodrome(
        self, cheval_id: int, hippodrome_id: int, exclure_course_id: int
    ) -> tuple[int, int]:
        """(victoires, courses) du cheval à cet hippodrome hors course en cours
        d'analyse — cf. L031.2 famille Historique (cf. L031.1 §5 : Historique = Hippodrome)."""
        with self._conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) FILTER (WHERE r.classement = 1 AND NOT r.disqualification), COUNT(*)
                FROM partant p
                JOIN resultat r ON r.partant_id = p.id
                JOIN course c ON c.id = p.course_id
                JOIN reunion re ON re.id = c.reunion_id
                WHERE p.cheval_id = %s AND re.hippodrome_id = %s AND p.course_id != %s AND NOT r.non_partant
                """,
                (cheval_id, hippodrome_id, exclure_course_id),
            )
            return cur.fetchone()

    def compter_performances_cheval_conditions(
        self, cheval_id: int, distance_id: int, surface_id: int, etat_piste_id: int, exclure_course_id: int
    ) -> tuple[int, int]:
        """(victoires, courses) du cheval dans les mêmes distance/surface/état de
        piste, hors course en cours d'analyse — cf. L031.2 famille Aptitude."""
        with self._conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) FILTER (WHERE r.classement = 1 AND NOT r.disqualification), COUNT(*)
                FROM partant p
                JOIN resultat r ON r.partant_id = p.id
                JOIN course c ON c.id = p.course_id
                WHERE p.cheval_id = %s AND c.distance_id = %s AND c.surface_id = %s AND c.etat_piste_id = %s
                  AND p.course_id != %s AND NOT r.non_partant
                """,
                (cheval_id, distance_id, surface_id, etat_piste_id, exclure_course_id),
            )
            return cur.fetchone()

    def update_reunion(self, reunion_id: int, champs: dict) -> Reunion | None:
        return self._mettre_a_jour(
            "reunion", "id, date, hippodrome_id, numero, heure_debut, heure_fin, statut", Reunion, reunion_id, champs
        )

    def update_course(self, course_id: int, champs: dict) -> Course | None:
        return self._mettre_a_jour(
            "course",
            "id, reunion_id, numero, nom, heure_depart, discipline_id, type_course_id, "
            "distance_id, surface_id, etat_piste_id, allocation, nb_partants, quinte",
            Course,
            course_id,
            champs,
        )

    def update_partant(self, partant_id: int, champs: dict) -> Partant | None:
        return self._mettre_a_jour(
            "partant",
            "id, course_id, cheval_id, jockey_id, entraineur_id, numero, corde, poids, "
            "valeur, age, ferrure, musique, non_partant",
            Partant,
            partant_id,
            champs,
        )

    def update_cheval(self, cheval_id: int, champs: dict) -> Cheval | None:
        return self._mettre_a_jour(
            "cheval", "id, nom, sexe, date_naissance, pere, mere, gains, musique, actif", Cheval, cheval_id, champs
        )

    def update_jockey(self, jockey_id: int, champs: dict) -> Jockey | None:
        return self._mettre_a_jour("jockey", "id, nom, prenom, licence, actif", Jockey, jockey_id, champs)

    def update_entraineur(self, entraineur_id: int, champs: dict) -> Entraineur | None:
        return self._mettre_a_jour("entraineur", "id, nom, prenom, actif", Entraineur, entraineur_id, champs)
