"""Repository du module Historique — cf. L018 §8, L015 §6.

Recherche transversale en lecture seule : une ligne par pari (avec l'analyse et
le contrôle ROI qui s'y rattachent), cf. `src/models/historique.py`.
"""

from __future__ import annotations

import psycopg
from psycopg.rows import class_row

from src.models.historique import HistoriqueFiltres, HistoriqueLigne

_COLONNES = """
    re.date AS date, re.hippodrome_id AS hippodrome_id, h.nom AS hippodrome_nom,
    c.id AS course_id, c.numero AS course_numero, c.nom AS course_nom,
    a.id AS analyse_id, a.version AS version, a.date_calcul AS date_calcul, a.decision AS decision,
    a.score_confiance AS score_confiance, a.risque AS risque, a.budget AS budget,
    p.id AS pari_id, p.type_pari AS type_pari, p.mise AS mise,
    p.gain_estime AS gain_estime, p.roi_estime AS roi_estime,
    crp.roi AS roi_reel, crp.profit AS profit_reel, crp.valide AS valide
"""


class HistoriqueRepository:
    def __init__(self, conn: psycopg.Connection) -> None:
        self._conn = conn

    def rechercher(self, filtres: HistoriqueFiltres) -> list[HistoriqueLigne]:
        conditions = []
        valeurs: list[object] = []
        if filtres.date_debut is not None:
            conditions.append("re.date >= %s")
            valeurs.append(filtres.date_debut)
        if filtres.date_fin is not None:
            conditions.append("re.date <= %s")
            valeurs.append(filtres.date_fin)
        if filtres.hippodrome_id is not None:
            conditions.append("re.hippodrome_id = %s")
            valeurs.append(filtres.hippodrome_id)
        if filtres.type_pari is not None:
            conditions.append("p.type_pari = %s")
            valeurs.append(filtres.type_pari)
        if filtres.decisions:
            conditions.append("a.decision = ANY(%s)")
            valeurs.append(filtres.decisions)

        clause_where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        valeurs.append(filtres.limite)

        with self._conn.cursor(row_factory=class_row(HistoriqueLigne)) as cur:
            cur.execute(
                f"""
                SELECT {_COLONNES}
                FROM reunion re
                JOIN course c ON c.reunion_id = re.id
                JOIN hippodrome h ON h.id = re.hippodrome_id
                -- Seule la dernière version d'analyse de chaque course (cf.
                -- L033 : la réanalyse horaire crée une nouvelle version à
                -- chaque passage, sans quoi une même course apparaîtrait une
                -- fois par version calculée dans la journée).
                JOIN analyses a ON a.course_id = c.id
                    AND a.version = (SELECT MAX(a2.version) FROM analyses a2 WHERE a2.course_id = c.id)
                LEFT JOIN pari p ON p.analyse_id = a.id
                LEFT JOIN controle_roi_pari crp ON crp.pari_id = p.id
                {clause_where}
                ORDER BY re.date DESC, c.numero, p.id
                LIMIT %s
                """,
                valeurs,
            )
            return cur.fetchall()
