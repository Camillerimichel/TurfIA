"""Collecte manuelle du programme hippique du jour (adaptateur PMU) — cf. plan de
collecte. Usage :

    python scripts/collecter_programme.py [--date DDMMYYYY]

Pas d'intégration à un ordonnanceur dans cette tranche (L017/L033 restent hors
périmètre, cf. PROJECT_STATE.md).
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime

from src.collecte.pmu.client import PMUClient
from src.database.connection import session
from src.repositories.course_repository import CourseRepository
from src.repositories.referentiel_repository import ReferentielRepository
from src.services.collecte_service import CollecteService


def parse_date(valeur: str) -> date:
    return datetime.strptime(valeur, "%d%m%Y").date()


def run() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", type=parse_date, default=date.today(), help="Format DDMMYYYY (défaut : aujourd'hui)")
    args = parser.parse_args()

    with PMUClient() as pmu_client, session() as conn:
        service = CollecteService(pmu_client, ReferentielRepository(conn), CourseRepository(conn))
        rapport = service.collecter_programme_du_jour(args.date)

    print(f"Réunions importées : {rapport.nb_reunions}")
    print(f"Courses importées  : {rapport.nb_courses}")
    print(f"Partants importés  : {rapport.nb_partants}")
    if rapport.erreurs:
        print(f"Erreurs ({len(rapport.erreurs)}) :")
        for erreur in rapport.erreurs:
            print(f"  - {erreur}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run())
