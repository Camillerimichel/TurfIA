"""Rafraîchit la collecte du jour puis relance l'analyse de toutes les
courses du jour (cf. L033 ADR-002 : mêmes services que l'API/l'Administration
HTML, jamais de logique dupliquée). Usage :

    python -m scripts.rafraichir_et_analyser_jour

Pensé pour un déclenchement périodique via launchd/cron locale (cf.
automations/launchd/, PROJECT_STATE.md — décision du 2026-07-09 : pas de
scheduler générique dans l'application elle-même, ce script est le
"traitement planifié" au sens de L017/L033, exécuté par l'OS).

Les cotes PMU se publient progressivement au fil de la journée : relancer la
collecte à chaque exécution permet de récupérer les cotes nouvellement
publiées pour des courses jusque-là sans partant exploitable (cf.
PreparationDonneesService, qui exclut plutôt que d'inventer une cote
manquante), avant de relancer l'analyse. Chaque étape est tracée dans
`tache` (même repository que `POST /administration/automatisations/*`) —
visible dans la page Administration au même titre qu'un déclenchement manuel.
"""

from __future__ import annotations

import sys
from datetime import date

from src.collecte.canalturf.client import CanalturfClient
from src.collecte.pmu.client import PMUClient
from src.collecte.zoneturf.client import ZoneTurfClient
from src.database.connection import session
from src.repositories.analyse_repository import AnalyseRepository
from src.repositories.course_repository import CourseRepository
from src.repositories.referentiel_repository import ReferentielRepository
from src.repositories.statistique_repository import StatistiqueRepository
from src.repositories.tache_repository import TacheRepository
from src.services.analyse_service import AnalyseService
from src.services.automatisation_service import AutomatisationService
from src.services.collecte_service import CollecteService
from src.services.consensus_presse_service import ConsensusPresseService
from src.services.preparation_service import PreparationDonneesService


def run() -> int:
    jour = date.today()

    with PMUClient() as pmu_client, CanalturfClient() as canalturf_client, ZoneTurfClient() as zoneturf_client:
        with session() as conn:
            tache_repo = TacheRepository(conn)
            course_repo = CourseRepository(conn)

            tache_collecte = tache_repo.demarrer("collecte_programme_jour", categorie="automatisation")
            try:
                collecte_service = CollecteService(pmu_client, ReferentielRepository(conn), course_repo)
                rapport_collecte = collecte_service.collecter_programme_du_jour(jour)
            except Exception as exc:
                tache_repo.terminer(tache_collecte.id, "echec", commentaire=str(exc)[:2000])
                raise
            tache_repo.terminer(
                tache_collecte.id,
                "succes",
                commentaire=(
                    f"{rapport_collecte.nb_reunions} réunion(s), {rapport_collecte.nb_courses} course(s), "
                    f"{rapport_collecte.nb_partants} partant(s)"
                ),
            )

            tache_analyse = tache_repo.demarrer("analyse_courses_jour", categorie="automatisation")
            try:
                presse = ConsensusPresseService(canalturf_client, zoneturf_client)
                preparation = PreparationDonneesService(course_repo, StatistiqueRepository(conn), presse)
                automatisation = AutomatisationService(
                    course_repo, preparation, AnalyseService(AnalyseRepository(conn))
                )
                rapport_analyse = automatisation.analyser_courses_du_jour(jour)
            except Exception as exc:
                tache_repo.terminer(tache_analyse.id, "echec", commentaire=str(exc)[:2000])
                raise
            statut = "succes" if rapport_analyse.nb_erreurs == 0 else "echec"
            tache_repo.terminer(
                tache_analyse.id,
                statut,
                commentaire=(
                    f"{rapport_analyse.nb_courses} course(s), {rapport_analyse.nb_deja_analysees} déjà à jour, "
                    f"{rapport_analyse.nb_erreurs} erreur(s)"
                ),
            )

    print(
        f"Collecte : {rapport_collecte.nb_reunions} réunion(s), {rapport_collecte.nb_courses} course(s), "
        f"{rapport_collecte.nb_partants} partant(s)"
    )
    for erreur in rapport_collecte.erreurs:
        print(f"  - {erreur}")
    print(
        f"Analyse : {rapport_analyse.nb_courses} course(s) analysée(s), "
        f"{rapport_analyse.nb_deja_analysees} déjà à jour, {rapport_analyse.nb_erreurs} erreur(s)"
    )
    for course_id, message in rapport_analyse.erreurs:
        print(f"  - Course {course_id} : {message}")
    return 0


if __name__ == "__main__":
    sys.exit(run())
