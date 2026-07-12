"""Repository du module Historique — cf. L018 §8, L015 §6.

Recherche transversale en lecture seule : une ligne par pari (avec l'analyse et
le contrôle ROI qui s'y rattachent), cf. `src/models/historique.py`.
"""

from __future__ import annotations

import psycopg
from psycopg.rows import class_row

from src.models.historique import GainRecentLigne, HistoriqueFiltres, HistoriqueLigne, ParisEnCoursLigne

_COLONNES = """
    re.date AS date, re.hippodrome_id AS hippodrome_id, h.nom AS hippodrome_nom,
    c.id AS course_id, c.numero AS course_numero, c.nom AS course_nom, c.heure_depart AS heure_depart,
    a.id AS analyse_id, a.version AS version, a.date_calcul AS date_calcul, a.decision AS decision,
    a.score_confiance AS score_confiance, a.risque AS risque, a.budget AS budget,
    p.id AS pari_id, p.type_pari AS type_pari, p.mise AS mise,
    p.gain_estime AS gain_estime, p.roi_estime AS roi_estime,
    crp.gains AS gains_reel, crp.roi AS roi_reel, crp.profit AS profit_reel, crp.valide AS valide
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
                -- Seule l'analyse RETENUE de chaque course (cf. L033 : la
                -- réanalyse horaire crée une nouvelle version à chaque
                -- passage, sans quoi une même course apparaîtrait une fois
                -- par version calculée dans la journée) — la sélection
                -- manuelle si elle existe (retour utilisateur, 2026-07-12),
                -- sinon la dernière version (comportement historique).
                JOIN analyses a ON a.course_id = c.id
                    AND a.id = COALESCE(
                        (SELECT sel.analyse_id FROM analyse_selection sel WHERE sel.course_id = c.id),
                        (SELECT a2.id FROM analyses a2 WHERE a2.course_id = c.id ORDER BY a2.version DESC LIMIT 1)
                    )
                LEFT JOIN pari p ON p.analyse_id = a.id
                LEFT JOIN controle_roi_pari crp ON crp.pari_id = p.id
                {clause_where}
                -- Retour utilisateur (2026-07-12, correction du tri initial) :
                -- la date la plus récente en premier (re.date DESC), puis à
                -- l'intérieur d'une même date les courses dans l'ordre
                -- chronologique naturel de la journée (c.heure_depart ASC,
                -- la première course du matin avant la dernière du soir) —
                -- pas un tri global unique sur l'horodatage complet, qui
                -- mélangeait les jours entre eux par heure de la journée.
                -- NULLS LAST : une course sans heure connue (donnée pas
                -- encore collectée) passe après celles qui en ont une.
                ORDER BY re.date DESC, c.heure_depart ASC NULLS LAST, c.numero, p.id
                LIMIT %s
                """,
                valeurs,
            )
            return cur.fetchall()

    def list_paris_en_cours(self) -> list[ParisEnCoursLigne]:
        """Courses dont la dernière analyse engage un budget réel (`budget > 0`)
        mais qui ne sont pas encore parties — cf. page Accueil, bloc « ROI
        global » (retour utilisateur : « mets la liste des paris en cours à
        surveiller avant leur course avec un lien... vers la course »).
        Restreint à l'analyse retenue de chaque course, même raison que
        `rechercher` (sélection manuelle sinon dernière version, cf. L033,
        réanalyse horaire à version croissante)."""
        with self._conn.cursor(row_factory=class_row(ParisEnCoursLigne)) as cur:
            cur.execute(
                """
                SELECT c.id AS course_id, c.numero AS course_numero, c.nom AS course_nom,
                       c.heure_depart AS heure_depart, h.nom AS hippodrome_nom,
                       a.id AS analyse_id, a.decision AS decision,
                       a.score_confiance AS score_confiance, a.budget AS budget
                FROM course c
                JOIN reunion re ON re.id = c.reunion_id
                JOIN hippodrome h ON h.id = re.hippodrome_id
                JOIN analyses a ON a.course_id = c.id
                    AND a.id = COALESCE(
                        (SELECT sel.analyse_id FROM analyse_selection sel WHERE sel.course_id = c.id),
                        (SELECT a2.id FROM analyses a2 WHERE a2.course_id = c.id ORDER BY a2.version DESC LIMIT 1)
                    )
                WHERE a.budget > 0
                  AND (c.heure_depart IS NULL OR c.heure_depart > now())
                ORDER BY c.heure_depart NULLS LAST
                """
            )
            return cur.fetchall()

    def list_gains_recents(self, heures: int = 24) -> list[GainRecentLigne]:
        """Courses arrivées dans les `heures` dernières heures (défaut 24,
        borne assumée pour un widget d'accueil — pas d'historique complet,
        cf. page Historique pour ça) dont le gain réel est déjà connu
        (`controle_roi`, calculé par `ControleRoiService.
        calculer_controles_manquants`) — cf. page Accueil, bloc « Gains
        récents » (retour utilisateur : « implémenter la récupération des
        gains dans Accueil »). `JOIN controle_roi` (pas `LEFT JOIN`) : une
        course sans contrôle pas encore calculé n'apparaît simplement pas
        ici, elle reste dans « Paris en cours » tant que son départ est
        futur, ou disparaît des deux tant que son contrôle n'est pas encore
        fait — pas d'état intermédiaire à afficher. Restreint à l'analyse
        retenue de chaque course, même raison que `list_paris_en_cours`."""
        with self._conn.cursor(row_factory=class_row(GainRecentLigne)) as cur:
            cur.execute(
                """
                SELECT c.id AS course_id, c.numero AS course_numero, c.nom AS course_nom,
                       c.heure_depart AS heure_depart, h.nom AS hippodrome_nom,
                       a.id AS analyse_id, a.decision AS decision,
                       cr.mise AS mise, cr.gains AS gains, cr.profit AS profit, cr.roi AS roi, cr.valide AS valide
                FROM course c
                JOIN reunion re ON re.id = c.reunion_id
                JOIN hippodrome h ON h.id = re.hippodrome_id
                JOIN analyses a ON a.course_id = c.id
                    AND a.id = COALESCE(
                        (SELECT sel.analyse_id FROM analyse_selection sel WHERE sel.course_id = c.id),
                        (SELECT a2.id FROM analyses a2 WHERE a2.course_id = c.id ORDER BY a2.version DESC LIMIT 1)
                    )
                JOIN controle_roi cr ON cr.analyse_id = a.id
                WHERE c.heure_depart IS NOT NULL
                  AND c.heure_depart <= now()
                  AND c.heure_depart >= now() - (%s * INTERVAL '1 hour')
                ORDER BY c.heure_depart DESC
                """,
                (heures,),
            )
            return cur.fetchall()
