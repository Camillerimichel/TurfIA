"""Repository des tables d'analyses — cf. L015 §6, L030.3.

Aucune méthode de mise à jour n'est exposée : les analyses sont immuables après
création (cf. ADR-002 de L001, L030.3 §1). Un recalcul crée une nouvelle version.
"""

from __future__ import annotations

import psycopg
from psycopg.rows import class_row

from src.core.exceptions import BusinessRuleError
from src.models.analyse import Analyse, AnalysePartant, ControleRoi, ControleRoiPari, Pari, Selection


class AnalyseRepository:
    def __init__(self, conn: psycopg.Connection) -> None:
        self._conn = conn

    def create_analyse(self, analyse: Analyse) -> Analyse:
        # `conn.transaction()` ouvre un SAVEPOINT : en cas de UniqueViolation
        # (course_id, version) déjà analysée), seul ce SAVEPOINT est annulé —
        # la transaction englobante (ex. AutomatisationService.
        # analyser_courses_du_jour, qui traite plusieurs courses dans une même
        # connexion/transaction) reste utilisable pour les courses suivantes.
        # Sans ce SAVEPOINT, une seule course déjà analysée avortait toute la
        # transaction ("current transaction is aborted"), donc tout le lot
        # (vérifié réellement : 500 sur /administration/automatisations/
        # analyse-jour dès qu'une course avait déjà une analyse en version 1).
        try:
            with self._conn.transaction():
                with self._conn.cursor(row_factory=class_row(Analyse)) as cur:
                    cur.execute(
                        """
                        INSERT INTO analyses (
                            course_id, version, score_confiance, risque, roi_theorique,
                            decision, budget, commentaire
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id, course_id, version, date_calcul, score_confiance, risque,
                                  roi_theorique, decision, budget, commentaire
                        """,
                        (
                            analyse.course_id,
                            analyse.version,
                            analyse.score_confiance,
                            analyse.risque,
                            analyse.roi_theorique,
                            analyse.decision,
                            analyse.budget,
                            analyse.commentaire,
                        ),
                    )
                    return cur.fetchone()
        except psycopg.errors.UniqueViolation as exc:
            raise BusinessRuleError(
                f"Une analyse existe déjà pour la course {analyse.course_id} en version {analyse.version}."
            ) from exc

    def existe_analyse(self, course_id: int, version: int) -> bool:
        """Vérifie à l'avance si `(course_id, version)` a déjà une analyse —
        cf. `AutomatisationService.analyser_courses_du_jour`, qui relance
        l'analyse du jour à chaque exécution horaire (L033) : sans ce
        contrôle, une course déjà analysée ne provoque une `BusinessRuleError`
        (cf. `create_analyse`) qu'après avoir refait tout le travail de
        préparation, et ce cas pourtant attendu (déjà traité à l'heure
        précédente) était compté comme une vraie erreur."""
        with self._conn.cursor() as cur:
            cur.execute("SELECT 1 FROM analyses WHERE course_id = %s AND version = %s LIMIT 1", (course_id, version))
            return cur.fetchone() is not None

    def get_analyse(self, analyse_id: int) -> Analyse | None:
        with self._conn.cursor(row_factory=class_row(Analyse)) as cur:
            cur.execute(
                """
                SELECT id, course_id, version, date_calcul, score_confiance, risque,
                       roi_theorique, decision, budget, commentaire
                FROM analyses WHERE id = %s
                """,
                (analyse_id,),
            )
            return cur.fetchone()

    def list_analyses_by_course(self, course_id: int) -> list[Analyse]:
        with self._conn.cursor(row_factory=class_row(Analyse)) as cur:
            cur.execute(
                """
                SELECT id, course_id, version, date_calcul, score_confiance, risque,
                       roi_theorique, decision, budget, commentaire
                FROM analyses WHERE course_id = %s ORDER BY version
                """,
                (course_id,),
            )
            return cur.fetchall()

    def create_analyse_partant(self, ap: AnalysePartant) -> AnalysePartant:
        with self._conn.cursor(row_factory=class_row(AnalysePartant)) as cur:
            cur.execute(
                """
                INSERT INTO analyse_partant (
                    analyse_id, partant_id, score, rang, consensus, evolution_cote,
                    value_bet, confiance, commentaire
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, analyse_id, partant_id, score, rang, consensus,
                          evolution_cote, value_bet, confiance, commentaire
                """,
                (
                    ap.analyse_id,
                    ap.partant_id,
                    ap.score,
                    ap.rang,
                    ap.consensus,
                    ap.evolution_cote,
                    ap.value_bet,
                    ap.confiance,
                    ap.commentaire,
                ),
            )
            return cur.fetchone()

    def list_analyse_partants(self, analyse_id: int) -> list[AnalysePartant]:
        with self._conn.cursor(row_factory=class_row(AnalysePartant)) as cur:
            cur.execute(
                """
                SELECT id, analyse_id, partant_id, score, rang, consensus,
                       evolution_cote, value_bet, confiance, commentaire
                FROM analyse_partant WHERE analyse_id = %s ORDER BY rang
                """,
                (analyse_id,),
            )
            return cur.fetchall()

    def create_selection(self, selection: Selection) -> Selection:
        with self._conn.cursor(row_factory=class_row(Selection)) as cur:
            cur.execute(
                """
                INSERT INTO selection (analyse_id, partant_id, categorie, ordre_affichage)
                VALUES (%s, %s, %s, %s)
                RETURNING id, analyse_id, partant_id, categorie, ordre_affichage
                """,
                (selection.analyse_id, selection.partant_id, selection.categorie, selection.ordre_affichage),
            )
            return cur.fetchone()

    def create_pari(self, pari: Pari) -> Pari:
        with self._conn.cursor(row_factory=class_row(Pari)) as cur:
            cur.execute(
                """
                INSERT INTO pari (analyse_id, type_pari, combinaison, mise, gain_estime, roi_estime)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, analyse_id, type_pari, combinaison, mise, gain_estime, roi_estime
                """,
                (pari.analyse_id, pari.type_pari, pari.combinaison, pari.mise, pari.gain_estime, pari.roi_estime),
            )
            return cur.fetchone()

    def list_selections_by_analyse(self, analyse_id: int) -> list[Selection]:
        with self._conn.cursor(row_factory=class_row(Selection)) as cur:
            cur.execute(
                """
                SELECT id, analyse_id, partant_id, categorie, ordre_affichage
                FROM selection WHERE analyse_id = %s ORDER BY ordre_affichage
                """,
                (analyse_id,),
            )
            return cur.fetchall()

    def list_paris_by_analyse(self, analyse_id: int) -> list[Pari]:
        with self._conn.cursor(row_factory=class_row(Pari)) as cur:
            cur.execute(
                """
                SELECT id, analyse_id, type_pari, combinaison, mise, gain_estime, roi_estime
                FROM pari WHERE analyse_id = %s
                """,
                (analyse_id,),
            )
            return cur.fetchall()

    def list_analyses_sans_controle_roi(self) -> list[Analyse]:
        """Analyses ayant au moins un pari (donc une mise réellement engagée) mais
        pas encore de `controle_roi` — cf. `ControleRoiService`."""
        with self._conn.cursor(row_factory=class_row(Analyse)) as cur:
            cur.execute(
                """
                SELECT a.id, a.course_id, a.version, a.date_calcul, a.score_confiance, a.risque,
                       a.roi_theorique, a.decision, a.budget, a.commentaire
                FROM analyses a
                LEFT JOIN controle_roi cr ON cr.analyse_id = a.id
                WHERE cr.id IS NULL AND EXISTS (SELECT 1 FROM pari p WHERE p.analyse_id = a.id)
                ORDER BY a.id
                """
            )
            return cur.fetchall()

    def create_controle_roi(self, controle: ControleRoi) -> ControleRoi:
        with self._conn.cursor(row_factory=class_row(ControleRoi)) as cur:
            cur.execute(
                """
                INSERT INTO controle_roi (analyse_id, mise, gains, profit, roi, valide, commentaire)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, analyse_id, mise, gains, profit, roi, valide, commentaire
                """,
                (
                    controle.analyse_id,
                    controle.mise,
                    controle.gains,
                    controle.profit,
                    controle.roi,
                    controle.valide,
                    controle.commentaire,
                ),
            )
            return cur.fetchone()

    def create_controle_roi_pari(self, controle: ControleRoiPari) -> ControleRoiPari:
        with self._conn.cursor(row_factory=class_row(ControleRoiPari)) as cur:
            cur.execute(
                """
                INSERT INTO controle_roi_pari (pari_id, mise, gains, profit, roi, valide)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, pari_id, mise, gains, profit, roi, valide
                """,
                (controle.pari_id, controle.mise, controle.gains, controle.profit, controle.roi, controle.valide),
            )
            return cur.fetchone()
