"""Repository des tables d'authentification (utilisateur, role, session) — cf.
L015 §6, L030.5, L021.
"""

from __future__ import annotations

import psycopg
from psycopg.rows import class_row

from src.models.utilisateur import Role, Session, Utilisateur


class UtilisateurRepository:
    def __init__(self, conn: psycopg.Connection) -> None:
        self._conn = conn

    def get_role_par_nom(self, nom: str) -> Role | None:
        with self._conn.cursor(row_factory=class_row(Role)) as cur:
            cur.execute("SELECT id, nom, description FROM role WHERE nom = %s", (nom,))
            return cur.fetchone()

    def get_role_par_id(self, role_id: int) -> Role | None:
        with self._conn.cursor(row_factory=class_row(Role)) as cur:
            cur.execute("SELECT id, nom, description FROM role WHERE id = %s", (role_id,))
            return cur.fetchone()

    def get_utilisateur_par_login(self, login: str) -> Utilisateur | None:
        with self._conn.cursor(row_factory=class_row(Utilisateur)) as cur:
            cur.execute(
                """
                SELECT id, login, mot_de_passe, nom, email, role_id, actif, derniere_connexion
                FROM utilisateur WHERE login = %s
                """,
                (login,),
            )
            return cur.fetchone()

    def creer_utilisateur(self, utilisateur: Utilisateur) -> Utilisateur:
        with self._conn.cursor(row_factory=class_row(Utilisateur)) as cur:
            cur.execute(
                """
                INSERT INTO utilisateur (login, mot_de_passe, nom, email, role_id, actif)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, login, mot_de_passe, nom, email, role_id, actif, derniere_connexion
                """,
                (
                    utilisateur.login,
                    utilisateur.mot_de_passe,
                    utilisateur.nom,
                    utilisateur.email,
                    utilisateur.role_id,
                    utilisateur.actif,
                ),
            )
            return cur.fetchone()

    def mettre_a_jour_derniere_connexion(self, utilisateur_id: int) -> None:
        with self._conn.cursor() as cur:
            cur.execute("UPDATE utilisateur SET derniere_connexion = now() WHERE id = %s", (utilisateur_id,))

    def creer_session(self, session: Session) -> Session:
        with self._conn.cursor(row_factory=class_row(Session)) as cur:
            cur.execute(
                """
                INSERT INTO session (utilisateur_id, jeton_hache, expire_le)
                VALUES (%s, %s, %s)
                RETURNING id, utilisateur_id, jeton_hache, expire_le, revoque_le, derniere_utilisation
                """,
                (session.utilisateur_id, session.jeton_hache, session.expire_le),
            )
            return cur.fetchone()

    def get_utilisateur_par_session_active(self, jeton_hache: str) -> tuple[Utilisateur, Role] | None:
        """Retourne (utilisateur, role) si le jeton correspond à une session non
        expirée, non révoquée, d'un utilisateur actif — sinon None. Une seule
        requête (jointure), appelée à chaque requête authentifiée."""
        with self._conn.cursor() as cur:
            cur.execute(
                """
                SELECT u.id, u.login, u.mot_de_passe, u.nom, u.email, u.role_id, u.actif, u.derniere_connexion,
                       r.id, r.nom, r.description
                FROM session s
                JOIN utilisateur u ON u.id = s.utilisateur_id
                JOIN role r ON r.id = u.role_id
                WHERE s.jeton_hache = %s
                  AND s.expire_le > now()
                  AND s.revoque_le IS NULL
                  AND u.actif
                """,
                (jeton_hache,),
            )
            ligne = cur.fetchone()
            if ligne is None:
                return None
            utilisateur = Utilisateur(
                id=ligne[0], login=ligne[1], mot_de_passe=ligne[2], nom=ligne[3],
                email=ligne[4], role_id=ligne[5], actif=ligne[6], derniere_connexion=ligne[7],
            )
            role = Role(id=ligne[8], nom=ligne[9], description=ligne[10])
            return utilisateur, role

    def marquer_utilisation_session(self, jeton_hache: str) -> None:
        with self._conn.cursor() as cur:
            cur.execute("UPDATE session SET derniere_utilisation = now() WHERE jeton_hache = %s", (jeton_hache,))

    def revoquer_session(self, jeton_hache: str) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                "UPDATE session SET revoque_le = now() WHERE jeton_hache = %s AND revoque_le IS NULL",
                (jeton_hache,),
            )
