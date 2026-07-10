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
manquante), avant de relancer l'analyse — qui vise systématiquement une
nouvelle version (cf. AnalyseService.prochaine_version) : la décision jouer/
ne pas jouer peut donc changer d'une heure à l'autre, dans les deux sens.
Troisième étape : contrôle ROI réel (rapports définitifs PMU) de chaque
analyse qui en manque encore, puis recalcul des 6 tables statistiques — cf.
`scripts/calculer_statistiques.py`, jusqu'ici déclenché uniquement à la main
(bouton Administration) ; intégré ici pour que les gains réels se mettent à
jour tout au long de la journée sans action manuelle (décision du
2026-07-10, cf. PROJECT_STATE.md — revient sur le "pas d'intégration à un
ordonnanceur" du 2026-07-09, qui ne visait que le scheduler générique, pas
cette réutilisation d'un script CLI déjà existant). Contrairement à
l'analyse, cette étape n'a pas de fenêtre de coupure : elle est justement
utile pour les courses déjà parties (`ControleRoiService` ignore déjà de
lui-même celles trop récentes, cf. MARGE_HOMOLOGATION_MINUTES).

Chaque étape est tracée dans `tache` (même repository que `POST
/administration/automatisations/*`) — visible dans la page Administration au
même titre qu'un déclenchement manuel.

Planifié toutes les heures de 9h à tard le soir (cf. automations/launchd/,
large pour couvrir les réunions en nocturne) mais l'étape d'analyse s'arrête
d'elle-même 30 minutes avant le départ de la dernière course du jour : au-delà,
les paris sont clos et une nouvelle version n'a plus d'utilité opérationnelle
(cf. CourseRepository.get_derniere_heure_depart).
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timedelta

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
from src.services.controle_roi_service import ControleRoiService
from src.services.preparation_service import PreparationDonneesService
from src.services.statistique_service import StatistiqueService

MARGE_AVANT_DERNIERE_COURSE_MINUTES = 30


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

            derniere_heure_depart = course_repo.get_derniere_heure_depart(jour)
            limite_analyse = (
                derniere_heure_depart - timedelta(minutes=MARGE_AVANT_DERNIERE_COURSE_MINUTES)
                if derniere_heure_depart is not None
                else None
            )
            if limite_analyse is not None and datetime.now() > limite_analyse:
                rapport_analyse = None
                tache_repo.terminer(
                    tache_analyse.id,
                    "succes",
                    commentaire=(
                        f"Hors fenêtre d'analyse (dernière course à {derniere_heure_depart:%H:%M}, "
                        f"limite {limite_analyse:%H:%M}) — aucune analyse relancée."
                    ),
                )
            else:
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
                        f"{rapport_analyse.nb_courses} course(s), {rapport_analyse.nb_deja_parties} déjà partie(s), "
                        f"{rapport_analyse.nb_erreurs} erreur(s)"
                    ),
                )

            tache_statistiques = tache_repo.demarrer("calcul_statistiques", categorie="automatisation")
            try:
                controle_roi_service = ControleRoiService(pmu_client, AnalyseRepository(conn), course_repo)
                controles = controle_roi_service.calculer_controles_manquants()
                resume_statistiques = StatistiqueService(StatistiqueRepository(conn)).calculer_toutes()
            except Exception as exc:
                tache_repo.terminer(tache_statistiques.id, "echec", commentaire=str(exc)[:2000])
                raise
            tache_repo.terminer(
                tache_statistiques.id,
                "succes",
                commentaire=f"{len(controles)} contrôle(s) ROI, tables : {resume_statistiques}",
            )

    print(
        f"Collecte : {rapport_collecte.nb_reunions} réunion(s), {rapport_collecte.nb_courses} course(s), "
        f"{rapport_collecte.nb_partants} partant(s)"
    )
    for erreur in rapport_collecte.erreurs:
        print(f"  - {erreur}")
    if rapport_analyse is None:
        print("Analyse : hors fenêtre (30 min avant la dernière course) — rien à faire.")
    else:
        print(
            f"Analyse : {rapport_analyse.nb_courses} course(s) analysée(s), "
            f"{rapport_analyse.nb_deja_parties} déjà partie(s), {rapport_analyse.nb_erreurs} erreur(s)"
        )
        for course_id, message in rapport_analyse.erreurs:
            print(f"  - Course {course_id} : {message}")
    print(f"Statistiques : {len(controles)} contrôle(s) ROI calculé(s), tables : {resume_statistiques}")
    return 0


if __name__ == "__main__":
    sys.exit(run())
