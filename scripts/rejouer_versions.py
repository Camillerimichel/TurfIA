"""Moteur de rejeu/backtesting (cf. L031.7 §4) — compare le ROI d'un jeu de
poids_score/poids_risque sur un historique de courses réelles déjà arrivées, à
budget constant. Usage :

    python scripts/rejouer_versions.py --version-modele "v2-marche-boost" \\
        --date-debut 2026-06-01 --date-fin 2026-07-01 \\
        --poids-score '{"marche": 1.5, "forme": 1.0}' \\
        --commentaire "Teste un marché renforcé"

Persiste une seule ligne de synthèse dans `statistique_modele` (ROI, taux de
réussite, paramètres utilisés) par exécution — ne modifie jamais `analyses`/
`pari`/`controle_roi` (choix de conception : persistance légère, cf.
PROJECT_STATE.md). Comparer plusieurs versions = exécuter ce script plusieurs
fois avec des `--version-modele`/poids différents, puis lire `GET
/statistiques/modeles` — cette même table est aussi alimentée par
`StatistiqueRepository.calculer_modeles` (agrégation des analyses déjà
persistées par `analyses.version`, une sémantique différente : cf. son
docstring), à ne pas confondre en lisant les résultats.

Hors périmètre (limites déjà existantes, héritées telles quelles) : le
consensus Presse n'est pas rejouable (`ConsensusPresseService` scrape en
direct, uniquement le Quinté+ du jour même) — non branché ici. Les familles
Value/Contexte ne sont jamais produites comme sous-scores. Les seuils de
décision (`determiner_decision`) ne sont pas paramétrables dans
`AnalyseService`, seuls les poids le sont — non rejouables.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date

from src.algorithms.rejeu import agreger_resultats_rejeu
from src.collecte.pmu.client import PMUClient
from src.core.exceptions import ImportationError, ValidationError
from src.core.logging import get_logger
from src.database.connection import session
from src.models.statistique import StatistiqueModele
from src.repositories.analyse_repository import AnalyseRepository
from src.repositories.course_repository import CourseRepository
from src.repositories.statistique_repository import StatistiqueRepository
from src.services.analyse_service import AnalyseService
from src.services.controle_roi_service import ControleRoiService
from src.services.preparation_service import PreparationDonneesService

logger = get_logger("rejeu")


def run() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version-modele", required=True, help="Identifiant descriptif de la version testée.")
    parser.add_argument("--date-debut", required=True, type=date.fromisoformat)
    parser.add_argument("--date-fin", required=True, type=date.fromisoformat)
    parser.add_argument("--poids-score", type=json.loads, default=None, help="JSON, ex. '{\"marche\": 1.5}'.")
    parser.add_argument("--poids-risque", type=json.loads, default=None, help="JSON.")
    parser.add_argument("--commentaire", default=None)
    args = parser.parse_args()

    with PMUClient() as pmu_client, session() as conn:
        course_repo = CourseRepository(conn)
        analyse_repo = AnalyseRepository(conn)
        preparation = PreparationDonneesService(course_repo)
        analyse_service = AnalyseService(analyse_repo, poids_score=args.poids_score, poids_risque=args.poids_risque)
        controle_roi_service = ControleRoiService(pmu_client, analyse_repo, course_repo)
        statistique_repo = StatistiqueRepository(conn)

        courses = course_repo.list_courses_avec_resultat(args.date_debut, args.date_fin)
        print(f"{len(courses)} course(s) éligible(s) au rejeu entre {args.date_debut} et {args.date_fin}.")

        resultats_paris: list[tuple[float, float, bool]] = []
        nb_courses_rejouees = 0
        for course in courses:
            try:
                donnees_partants, sous_risques_course = preparation.preparer_donnees_partants(course.id)
            except ValidationError as exc:
                logger.warning(f"Course {course.id} ignorée (préparation) : {exc}")
                continue

            resultat = analyse_service.analyser_course(
                course_id=course.id,
                version=1,
                partants=donnees_partants,
                sous_risques_course=sous_risques_course,
                persister=False,
            )
            if not resultat.paris:
                continue

            reunion = course_repo.get_reunion(course.reunion_id)
            try:
                rapports_bruts = pmu_client.recuperer_rapports_definitifs(reunion.date, reunion.numero, course.numero)
            except ImportationError as exc:
                logger.warning(f"Rapports PMU indisponibles pour la course {course.id} : {exc}")
                continue

            cache: dict[str, tuple] = {}
            nb_courses_rejouees += 1
            for pari in resultat.paris:
                gains = controle_roi_service.calculer_gains_pari(pari, rapports_bruts, cache, analyse_id=None)
                if gains is None:
                    continue
                mise = float(pari.mise)
                resultats_paris.append((mise, gains, gains > mise))

        nb_paris, roi, taux_reussite = agreger_resultats_rejeu(resultats_paris)
        parametres = json.dumps({"poids_score": args.poids_score, "poids_risque": args.poids_risque})
        stat = statistique_repo.create_modele(
            StatistiqueModele(
                version_modele=args.version_modele,
                date_debut=args.date_debut,
                date_fin=args.date_fin,
                nb_courses=nb_courses_rejouees,
                roi=roi,
                taux_reussite=taux_reussite,
                parametres=parametres,
                commentaire=args.commentaire,
            )
        )

    print(f"Version « {stat.version_modele} » — {stat.nb_courses} course(s) rejouée(s), {nb_paris} pari(s) contrôlé(s).")
    print(f"ROI : {stat.roi if stat.roi is not None else 'n/a'}")
    print(f"Taux de réussite : {stat.taux_reussite if stat.taux_reussite is not None else 'n/a'}")
    return 0


if __name__ == "__main__":
    sys.exit(run())
