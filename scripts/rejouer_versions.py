"""Moteur de rejeu/backtesting (cf. L031.7 §4) — compare le ROI d'un jeu de
poids_score/poids_risque sur un historique de courses réelles déjà arrivées, à
budget constant. Usage :

    python scripts/rejouer_versions.py --version-modele "v2-marche-boost" \\
        --date-debut 2026-06-01 --date-fin 2026-07-01 \\
        --poids-score '{"marche": 1.5, "forme": 1.0}' \\
        --commentaire "Teste un marché renforcé"

Fin implémentation dans `src.services.rejeu_service.RejeuService` — ce script
n'est plus qu'un point d'entrée CLI (même service que `POST
/administration/rejeu`, aucune logique dupliquée, cf. L033 ADR-002).

Persiste une seule ligne de synthèse dans `statistique_modele` par exécution
(`source="rejeu"`) — ne modifie jamais `analyses`/`pari`/`controle_roi` (choix
de conception : persistance légère, cf. PROJECT_STATE.md). Couvre les 7
indicateurs L031.7 §5 : ROI global, ROI par tranche de score/hippodrome/type
de pari (JSON, cf. `src/algorithms/rejeu.py`), taux de réussite, drawdown,
stabilité. Comparer plusieurs versions = exécuter ce script plusieurs fois
avec des `--version-modele`/poids différents, puis lire `GET
/statistiques/modeles` — cette même table est aussi alimentée par
`StatistiqueRepository.calculer_modeles` (agrégation des analyses déjà
persistées par `analyses.version`, `source="automatique"`, une sémantique
différente, sans ces 5 indicateurs supplémentaires : cf. son docstring), à ne
pas confondre en lisant les résultats — désormais distingué par la colonne
`source`.

Hors périmètre (limites déjà existantes, héritées telles quelles) : le
consensus Presse n'est pas rejouable (`ConsensusPresseService` scrape en
direct, uniquement le Quinté+ du jour même) — non branché ici. La famille
Historique (cf. `calculer_indicateur_historique_moteur`) reflète l'état
*actuel* de `statistique_hippodrome`, pas un instantané au moment de la
course rejouée — même limite que Marché/Presse/Professionnels, qui lisent
déjà tous des données à leur état présent plutôt qu'un instantané historique.
Les familles Value/Contexte ne sont jamais produites comme sous-scores. Les seuils de
décision (`determiner_decision`) ne sont pas paramétrables dans
`AnalyseService`, seuls les poids le sont — non rejouables.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date

from src.collecte.pmu.client import PMUClient
from src.database.connection import session
from src.repositories.analyse_repository import AnalyseRepository
from src.repositories.course_repository import CourseRepository
from src.repositories.statistique_repository import StatistiqueRepository
from src.services.rejeu_service import RejeuService


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
        service = RejeuService(
            pmu_client, CourseRepository(conn), AnalyseRepository(conn), StatistiqueRepository(conn)
        )
        stat = service.rejouer(
            version_modele=args.version_modele,
            date_debut=args.date_debut,
            date_fin=args.date_fin,
            poids_score=args.poids_score,
            poids_risque=args.poids_risque,
            commentaire=args.commentaire,
        )

    print(f"Version « {stat.version_modele} » — {stat.nb_courses} course(s) rejouée(s).")
    print(f"ROI : {stat.roi if stat.roi is not None else 'n/a'}")
    print(f"Taux de réussite : {stat.taux_reussite if stat.taux_reussite is not None else 'n/a'}")
    print(f"Drawdown : {stat.drawdown if stat.drawdown is not None else 'n/a'}")
    print(f"Stabilité (écart-type ROI) : {stat.stabilite if stat.stabilite is not None else 'n/a'}")
    return 0


if __name__ == "__main__":
    sys.exit(run())
