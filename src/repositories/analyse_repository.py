"""Repository des tables d'analyse — cf. L015 §6, L030.3.

Aucune méthode de mise à jour n'est exposée : les analyses sont immuables après
création (cf. ADR-002 de L001, L030.3 §1). Un recalcul crée une nouvelle version.
"""

from __future__ import annotations

import psycopg
from psycopg.rows import class_row

from src.models.analyse import Analyse, AnalysePartant, ControleRoi, Pari, Selection


class AnalyseRepository:
    def __init__(self, conn: psycopg.Connection) -> None:
        self._conn = conn

    def create_analyse(self, analyse: Analyse) -> Analyse:
        with self._conn.cursor(row_factory=class_row(Analyse)) as cur:
            cur.execute(
                """
                INSERT INTO analyse (
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

    def get_analyse(self, analyse_id: int) -> Analyse | None:
        with self._conn.cursor(row_factory=class_row(Analyse)) as cur:
            cur.execute(
                """
                SELECT id, course_id, version, date_calcul, score_confiance, risque,
                       roi_theorique, decision, budget, commentaire
                FROM analyse WHERE id = %s
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
                FROM analyse WHERE course_id = %s ORDER BY version
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
