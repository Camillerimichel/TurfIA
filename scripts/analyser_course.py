"""Déclenche une analyse à partir des données déjà collectées (cf.
scripts/collecter_programme.py) pour une course donnée. Usage :

    python scripts/analyser_course.py --course-id 42
"""

from __future__ import annotations

import argparse
import sys

from src.database.connection import session
from src.repositories.analyse_repository import AnalyseRepository
from src.repositories.course_repository import CourseRepository
from src.services.analyse_service import AnalyseService
from src.services.preparation_service import PreparationDonneesService


def run() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--course-id", type=int, required=True)
    parser.add_argument("--version", type=int, default=1)
    args = parser.parse_args()

    with session() as conn:
        preparation = PreparationDonneesService(CourseRepository(conn))
        donnees_partants, sous_risques_course = preparation.preparer_donnees_partants(args.course_id)

        service = AnalyseService(AnalyseRepository(conn))
        resultat = service.analyser_course(
            course_id=args.course_id,
            version=args.version,
            partants=donnees_partants,
            sous_risques_course=sous_risques_course,
        )

    print(f"Analyse #{resultat.analyse.id} — course {args.course_id}")
    print(f"Score de confiance : {resultat.analyse.score_confiance}")
    print(f"Risque             : {resultat.analyse.risque}")
    print(f"Décision           : {resultat.analyse.decision}")
    print(f"Budget conseillé   : {resultat.analyse.budget}")
    print("Classement :")
    for pc in resultat.partants_classes:
        print(f"  {pc.rang}. partant {pc.partant_id} — {pc.categorie} (score final {pc.score_final:.1f})")
    return 0


if __name__ == "__main__":
    sys.exit(run())
