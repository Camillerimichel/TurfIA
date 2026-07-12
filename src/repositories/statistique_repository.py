"""Repository des tables statistiques — cf. L015 §6, L030.4.

Chaque table expose `calculer_X` (agrégation en lecture sur `controle_roi` et les
tables liées, ne persiste rien) puis `create_X` (INSERT — jamais d'UPDATE : un
recalcul insère toujours une nouvelle ligne, cf. L030.4 §10).
"""

from __future__ import annotations

import psycopg
from psycopg.rows import class_row

from src.algorithms.score import SEUILS_DECISION_PAR_DEFAUT
from src.models.statistique import (
    StatistiqueDiscipline,
    StatistiqueGlobale,
    StatistiqueHippodrome,
    StatistiqueModele,
    StatistiquePari,
    StatistiqueScore,
)


def _ratio_pourcentage(numerateur: float, denominateur: float) -> float | None:
    return (numerateur / denominateur) * 100 if denominateur else None


# Une course réanalysée plusieurs fois avant son départ (cf. L033,
# automatisation horaire à version croissante) ne doit compter qu'une fois
# dans les statistiques — jamais une fois par version historique. Bug réel
# corrigé le 2026-07-10 (cf. PROJECT_STATE.md) : `controle_roi` recevait une
# ligne par version dès qu'une course devenait éligible, gonflant nb_courses/
# mises/gains d'autant. `a` doit être l'alias de la table `analyses` dans la
# requête où ce filtre est inséré.
_DERNIERE_VERSION_COURSE = "a.version = (SELECT MAX(a2.version) FROM analyses a2 WHERE a2.course_id = a.course_id)"


class StatistiqueRepository:
    def __init__(self, conn: psycopg.Connection) -> None:
        self._conn = conn

    def calculer_globale(self) -> StatistiqueGlobale:
        """`taux_reussite` = % de courses (pas de paris individuels) dont le
        profit combiné de tous les paris est positif (`controle_roi.valide`,
        un agrégat par analyse) — même granularité que `calculer_scores`, mais
        différente de `calculer_paris` (`controle_roi_pari`, une ligne par
        pari) qui mesure le % de paris individuels gagnants. Même libellé
        « Taux de réussite » aux deux granularités, distingué côté affichage
        depuis le 2026-07-12 (« Taux de réussite (courses) » vs « (paris) »,
        retour utilisateur) — pas un bug, une ambiguïté de nommage clarifiée."""
        with self._conn.cursor() as cur:
            cur.execute("SELECT COUNT(DISTINCT course_id) FROM analyses")
            (nb_courses,) = cur.fetchone()
            cur.execute(
                f"""
                SELECT COUNT(DISTINCT course_id) FROM analyses a
                WHERE budget > 0 AND {_DERNIERE_VERSION_COURSE}
                """
            )
            (nb_jouees,) = cur.fetchone()
            cur.execute(
                f"""
                SELECT COALESCE(SUM(cr.mise), 0), COALESCE(SUM(cr.gains), 0), COUNT(*), COUNT(*) FILTER (WHERE cr.valide)
                FROM controle_roi cr
                JOIN analyses a ON a.id = cr.analyse_id
                WHERE {_DERNIERE_VERSION_COURSE}
                """
            )
            mises, gains, nb_controles, nb_valides = cur.fetchone()

        mises, gains = float(mises), float(gains)
        profit = gains - mises
        return StatistiqueGlobale(
            nb_courses=nb_courses,
            nb_jouees=nb_jouees,
            nb_ignorees=nb_courses - nb_jouees,
            mises=mises,
            gains=gains,
            profit=profit,
            roi=_ratio_pourcentage(profit, mises),
            taux_reussite=_ratio_pourcentage(nb_valides, nb_controles),
        )

    def create_globale(self, stat: StatistiqueGlobale) -> StatistiqueGlobale:
        with self._conn.cursor(row_factory=class_row(StatistiqueGlobale)) as cur:
            cur.execute(
                """
                INSERT INTO statistique_globale
                    (nb_courses, nb_jouees, nb_ignorees, mises, gains, profit, roi, taux_reussite)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, date_calcul, nb_courses, nb_jouees, nb_ignorees, mises, gains, profit, roi, taux_reussite
                """,
                (
                    stat.nb_courses,
                    stat.nb_jouees,
                    stat.nb_ignorees,
                    stat.mises,
                    stat.gains,
                    stat.profit,
                    stat.roi,
                    stat.taux_reussite,
                ),
            )
            return cur.fetchone()

    def calculer_scores(self) -> list[StatistiqueScore]:
        seuil_prudent, seuil_normal, seuil_opportunite = SEUILS_DECISION_PAR_DEFAUT
        tranches = [
            (0.0, seuil_prudent),
            (seuil_prudent, seuil_normal),
            (seuil_normal, seuil_opportunite),
            (seuil_opportunite, 100.0),
        ]
        resultats = []
        with self._conn.cursor() as cur:
            for index, (score_min, score_max) in enumerate(tranches):
                dernier = index == len(tranches) - 1
                operateur_max = "<=" if dernier else "<"
                cur.execute(
                    f"""
                    SELECT COUNT(*), COUNT(*) FILTER (WHERE cr.valide), COALESCE(SUM(cr.mise), 0), COALESCE(SUM(cr.gains), 0)
                    FROM controle_roi cr
                    JOIN analyses a ON a.id = cr.analyse_id
                    WHERE a.score_confiance >= %s AND a.score_confiance {operateur_max} %s
                      AND {_DERNIERE_VERSION_COURSE}
                    """,
                    (score_min, score_max),
                )
                nb_courses, nb_gagnantes, mises, gains = cur.fetchone()
                mises, gains = float(mises), float(gains)
                resultats.append(
                    StatistiqueScore(
                        score_min=score_min,
                        score_max=score_max,
                        nb_courses=nb_courses,
                        nb_gagnantes=nb_gagnantes,
                        roi=_ratio_pourcentage(gains - mises, mises),
                        taux_reussite=_ratio_pourcentage(nb_gagnantes, nb_courses),
                    )
                )
        return resultats

    def create_score(self, stat: StatistiqueScore) -> StatistiqueScore:
        with self._conn.cursor(row_factory=class_row(StatistiqueScore)) as cur:
            cur.execute(
                """
                INSERT INTO statistique_score (score_min, score_max, nb_courses, nb_gagnantes, roi, taux_reussite)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, score_min, score_max, nb_courses, nb_gagnantes, roi, taux_reussite
                """,
                (stat.score_min, stat.score_max, stat.nb_courses, stat.nb_gagnantes, stat.roi, stat.taux_reussite),
            )
            return cur.fetchone()

    def calculer_hippodromes(self) -> list[StatistiqueHippodrome]:
        with self._conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT re.hippodrome_id, COUNT(*), COALESCE(SUM(cr.mise), 0), COALESCE(SUM(cr.gains), 0)
                FROM controle_roi cr
                JOIN analyses a ON a.id = cr.analyse_id
                JOIN course c ON c.id = a.course_id
                JOIN reunion re ON re.id = c.reunion_id
                WHERE {_DERNIERE_VERSION_COURSE}
                GROUP BY re.hippodrome_id
                """
            )
            lignes = cur.fetchall()
        resultats = []
        for hippodrome_id, nb_courses, mises, gains in lignes:
            mises, gains = float(mises), float(gains)
            resultats.append(
                StatistiqueHippodrome(
                    hippodrome_id=hippodrome_id, nb_courses=nb_courses, mises=mises, gains=gains,
                    profit=gains - mises, roi=_ratio_pourcentage(gains - mises, mises),
                )
            )
        return resultats

    def create_hippodrome(self, stat: StatistiqueHippodrome) -> StatistiqueHippodrome:
        with self._conn.cursor(row_factory=class_row(StatistiqueHippodrome)) as cur:
            cur.execute(
                """
                INSERT INTO statistique_hippodrome (hippodrome_id, nb_courses, mises, gains, profit, roi)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, hippodrome_id, nb_courses, mises, gains, profit, roi
                """,
                (stat.hippodrome_id, stat.nb_courses, stat.mises, stat.gains, stat.profit, stat.roi),
            )
            return cur.fetchone()

    def get_dernier_hippodrome(self, hippodrome_id: int) -> StatistiqueHippodrome | None:
        """Dernière ligne calculée pour cet hippodrome (table historisée, jamais
        mise à jour en place) — alimente la famille Score « Historique » (cf.
        L031.2 §3, `src/algorithms/indicateurs.py::calculer_indicateur_historique_moteur`)."""
        with self._conn.cursor(row_factory=class_row(StatistiqueHippodrome)) as cur:
            cur.execute(
                """
                SELECT id, hippodrome_id, nb_courses, mises, gains, profit, roi
                FROM statistique_hippodrome WHERE hippodrome_id = %s ORDER BY id DESC LIMIT 1
                """,
                (hippodrome_id,),
            )
            return cur.fetchone()

    def calculer_disciplines(self) -> list[StatistiqueDiscipline]:
        with self._conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT c.discipline_id, COUNT(*), COALESCE(SUM(cr.mise), 0), COALESCE(SUM(cr.gains), 0)
                FROM controle_roi cr
                JOIN analyses a ON a.id = cr.analyse_id
                JOIN course c ON c.id = a.course_id
                WHERE c.discipline_id IS NOT NULL AND {_DERNIERE_VERSION_COURSE}
                GROUP BY c.discipline_id
                """
            )
            lignes = cur.fetchall()
        resultats = []
        for discipline_id, nb_courses, mises, gains in lignes:
            mises, gains = float(mises), float(gains)
            resultats.append(
                StatistiqueDiscipline(
                    discipline_id=discipline_id, nb_courses=nb_courses, mises=mises, gains=gains,
                    profit=gains - mises, roi=_ratio_pourcentage(gains - mises, mises),
                )
            )
        return resultats

    def create_discipline(self, stat: StatistiqueDiscipline) -> StatistiqueDiscipline:
        with self._conn.cursor(row_factory=class_row(StatistiqueDiscipline)) as cur:
            cur.execute(
                """
                INSERT INTO statistique_discipline (discipline_id, nb_courses, mises, gains, profit, roi)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, discipline_id, nb_courses, mises, gains, profit, roi
                """,
                (stat.discipline_id, stat.nb_courses, stat.mises, stat.gains, stat.profit, stat.roi),
            )
            return cur.fetchone()

    def calculer_paris(self) -> list[StatistiquePari]:
        """Regroupe par `pari.type_pari` — mise/gains/validité viennent de
        `controle_roi_pari` (une ligne par pari, cf. L011 §8.7), pas de
        `controle_roi` (un agrégat par analyse, insuffisant depuis qu'une analyse
        produit plusieurs types de pari, cf. `construire_paris` — corrigé le
        2026-07-08, cf. PROJECT_STATE.md)."""
        with self._conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT p.type_pari, COUNT(*), COUNT(*) FILTER (WHERE crp.valide),
                       COALESCE(SUM(crp.mise), 0), COALESCE(SUM(crp.gains), 0)
                FROM controle_roi_pari crp
                JOIN pari p ON p.id = crp.pari_id
                JOIN analyses a ON a.id = p.analyse_id
                WHERE {_DERNIERE_VERSION_COURSE}
                GROUP BY p.type_pari
                """
            )
            lignes = cur.fetchall()
        resultats = []
        for type_pari, nb_paris, nb_gagnants, mises, gains in lignes:
            mises, gains = float(mises), float(gains)
            resultats.append(
                StatistiquePari(
                    type_pari=type_pari, nb_paris=nb_paris, mises=mises, gains=gains,
                    profit=gains - mises, roi=_ratio_pourcentage(gains - mises, mises),
                    taux_reussite=_ratio_pourcentage(nb_gagnants, nb_paris),
                )
            )
        return resultats

    def create_pari_stat(self, stat: StatistiquePari) -> StatistiquePari:
        with self._conn.cursor(row_factory=class_row(StatistiquePari)) as cur:
            cur.execute(
                """
                INSERT INTO statistique_pari (type_pari, nb_paris, mises, gains, profit, roi, taux_reussite)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, type_pari, nb_paris, mises, gains, profit, roi, taux_reussite
                """,
                (stat.type_pari, stat.nb_paris, stat.mises, stat.gains, stat.profit, stat.roi, stat.taux_reussite),
            )
            return cur.fetchone()

    def calculer_modeles(self) -> list[StatistiqueModele]:
        """Agrège les analyses déjà persistées par `analyses.version` — **pas**
        une vraie version de modèle : cette colonne désigne le statut Pré/Finale
        d'une même exécution (cf. L030.3), pas un jeu de paramètres différent.
        Le vrai rejeu multi-versions (L031.7 §4) vit dans `scripts/
        rejouer_versions.py` (`version_modele` y est une chaîne libre décrivant
        le jeu de poids testé, sans lien avec `analyses.version`) — les deux
        alimentent la même table avec des sémantiques différentes, à ne pas
        confondre en lisant `GET /statistiques/modeles` (limite documentée,
        cf. PROJECT_STATE.md, non corrigée ici, hors périmètre). Le filtre
        `_DERNIERE_VERSION_COURSE` (cf. plus haut) reste appliqué même ici :
        sans lui, une course réanalysée plusieurs fois comptait plusieurs fois
        (une fois par ancienne version), gonflant plusieurs des buckets
        `a.version` simultanément — la confusion Pré/Finale vs jeu de
        paramètres demeure (hors périmètre), mais chaque course ne compte
        désormais qu'une fois, dans le bucket de sa version actuelle."""
        with self._conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT a.version, MIN(re.date), MAX(re.date), COUNT(*),
                       COUNT(*) FILTER (WHERE cr.valide), COALESCE(SUM(cr.mise), 0), COALESCE(SUM(cr.gains), 0)
                FROM controle_roi cr
                JOIN analyses a ON a.id = cr.analyse_id
                JOIN course c ON c.id = a.course_id
                JOIN reunion re ON re.id = c.reunion_id
                WHERE {_DERNIERE_VERSION_COURSE}
                GROUP BY a.version
                """
            )
            lignes = cur.fetchall()
        resultats = []
        for version, date_debut, date_fin, nb_courses, nb_valides, mises, gains in lignes:
            mises, gains = float(mises), float(gains)
            resultats.append(
                StatistiqueModele(
                    version_modele=str(version), date_debut=date_debut, date_fin=date_fin, nb_courses=nb_courses,
                    roi=_ratio_pourcentage(gains - mises, mises), taux_reussite=_ratio_pourcentage(nb_valides, nb_courses),
                    source="automatique",
                )
            )
        return resultats

    def create_modele(self, stat: StatistiqueModele) -> StatistiqueModele:
        with self._conn.cursor(row_factory=class_row(StatistiqueModele)) as cur:
            cur.execute(
                """
                INSERT INTO statistique_modele
                    (version_modele, date_debut, date_fin, nb_courses, roi, taux_reussite,
                     roi_par_score, roi_par_hippodrome, roi_par_type_pari, drawdown, stabilite,
                     parametres, commentaire, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, version_modele, date_debut, date_fin, nb_courses, roi, taux_reussite,
                          roi_par_score, roi_par_hippodrome, roi_par_type_pari, drawdown, stabilite,
                          parametres, commentaire, source, cree_le
                """,
                (
                    stat.version_modele,
                    stat.date_debut,
                    stat.date_fin,
                    stat.nb_courses,
                    stat.roi,
                    stat.taux_reussite,
                    stat.roi_par_score,
                    stat.roi_par_hippodrome,
                    stat.roi_par_type_pari,
                    stat.drawdown,
                    stat.stabilite,
                    stat.parametres,
                    stat.commentaire,
                    stat.source,
                ),
            )
            return cur.fetchone()

    def list_globale(self) -> list[StatistiqueGlobale]:
        """Une seule ligne : la plus récente. `statistique_globale` n'a pas de
        clé de regroupement naturelle (un seul agrégat global) — chaque
        recalcul horaire (cf. L033) insère une nouvelle ligne sans jamais
        remplacer l'ancienne (L030.4 §10, historique conservé pour audit),
        mais l'affichage ne doit montrer que l'état actuel, pas la pile de
        chaque passage horaire (bug réel signalé par l'utilisateur, cf.
        PROJECT_STATE.md : « je ne comprends rien », des dizaines de lignes
        quasi identiques après plusieurs jours d'automatisation horaire)."""
        with self._conn.cursor(row_factory=class_row(StatistiqueGlobale)) as cur:
            cur.execute(
                "SELECT id, date_calcul, nb_courses, nb_jouees, nb_ignorees, mises, gains, profit, roi, taux_reussite "
                "FROM statistique_globale ORDER BY date_calcul DESC LIMIT 1"
            )
            ligne = cur.fetchone()
            return [ligne] if ligne is not None else []

    def list_scores(self) -> list[StatistiqueScore]:
        return self._list_dernier_par_groupe(
            "statistique_score", StatistiqueScore,
            "id, score_min, score_max, nb_courses, nb_gagnantes, roi, taux_reussite",
            "score_min, score_max", "cree_le",
        )

    def list_hippodromes(self) -> list[StatistiqueHippodrome]:
        return self._list_dernier_par_groupe(
            "statistique_hippodrome", StatistiqueHippodrome,
            "id, hippodrome_id, nb_courses, mises, gains, profit, roi",
            "hippodrome_id", "cree_le",
        )

    def list_disciplines(self) -> list[StatistiqueDiscipline]:
        return self._list_dernier_par_groupe(
            "statistique_discipline", StatistiqueDiscipline,
            "id, discipline_id, nb_courses, mises, gains, profit, roi",
            "discipline_id", "cree_le",
        )

    def list_paris(self) -> list[StatistiquePari]:
        return self._list_dernier_par_groupe(
            "statistique_pari", StatistiquePari,
            "id, type_pari, nb_paris, mises, gains, profit, roi, taux_reussite",
            "type_pari", "cree_le",
        )

    def list_modeles(self) -> list[StatistiqueModele]:
        # Vrai bug trouvé et corrigé (2026-07-12) : ne sélectionnait pas
        # roi_par_score/roi_par_hippodrome/roi_par_type_pari/drawdown/
        # stabilite/parametres/source/cree_le — un rejeu réel
        # (scripts/rejouer_versions.py) les renseigne pourtant tous, mais
        # `GET /statistiques/modeles` ne les a jamais renvoyés : le détail
        # par tranche de score/hippodrome/type de pari de la page
        # Statistiques était donc systématiquement vide ("Non disponible
        # pour cette ligne"), quel que soit le contenu réel en base.
        return self._list_dernier_par_groupe(
            "statistique_modele", StatistiqueModele,
            "id, version_modele, date_debut, date_fin, nb_courses, roi, taux_reussite, commentaire, "
            "roi_par_score, roi_par_hippodrome, roi_par_type_pari, drawdown, stabilite, parametres, "
            "source, cree_le",
            "version_modele", "cree_le",
        )

    def _list_dernier_par_groupe(
        self, table: str, modele: type, colonnes: str, groupe_par: str, colonne_tri: str
    ) -> list:
        """Une ligne par valeur distincte de `groupe_par`, la plus récente (même
        raison que `list_globale` ci-dessus : l'historique complet reste en
        base, seul l'affichage se limite à l'état actuel). `table`/`colonnes`/
        `groupe_par`/`colonne_tri` sont toujours des littéraux fournis par le
        code appelant, jamais dérivés d'une entrée utilisateur."""
        with self._conn.cursor(row_factory=class_row(modele)) as cur:
            cur.execute(
                f"SELECT DISTINCT ON ({groupe_par}) {colonnes} FROM {table} "
                f"ORDER BY {groupe_par}, {colonne_tri} DESC"
            )
            return cur.fetchall()
