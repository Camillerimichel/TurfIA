"""Ferme la boucle collecte -> analyse -> résultat réel -> statistiques (cf.
L030.4, L011 §8.7). Usage :

    python scripts/calculer_statistiques.py

Enchaîne : (1) contrôle ROI réel de chaque analyse ayant un pari mais pas encore
de résultat validé (via les rapports définitifs PMU), (2) recalcul des 6 tables
statistiques à partir de l'ensemble des contrôles disponibles. Pas d'intégration
à un ordonnanceur dans cette tranche (L017/L033 hors périmètre).
"""

from __future__ import annotations

import sys

from src.collecte.pmu.client import PMUClient
from src.database.connection import session
from src.repositories.analyse_repository import AnalyseRepository
from src.repositories.course_repository import CourseRepository
from src.repositories.statistique_repository import StatistiqueRepository
from src.services.controle_roi_service import ControleRoiService
from src.services.statistique_service import StatistiqueService


def run() -> int:
    with PMUClient() as pmu_client, session() as conn:
        controle_roi_service = ControleRoiService(pmu_client, AnalyseRepository(conn), CourseRepository(conn))
        controles = controle_roi_service.calculer_controles_manquants()

        statistique_service = StatistiqueService(StatistiqueRepository(conn))
        resume = statistique_service.calculer_toutes()

    print(f"Contrôles ROI calculés : {len(controles)}")
    for controle in controles:
        print(f"  analyse #{controle.analyse_id} — profit {controle.profit:+.2f} € (ROI {controle.roi:+.1f}%)")
    print("Statistiques recalculées :")
    for table, nb_lignes in resume.items():
        print(f"  {table} : {nb_lignes} ligne(s)")
    return 0


if __name__ == "__main__":
    sys.exit(run())
