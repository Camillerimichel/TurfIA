"""Orchestration du calcul des tables statistiques — cf. L015 §7, L030.4.

Périmètre volontaire (cf. plan Statistiques) : agrégation des `controle_roi`/
`analyses` déjà persistés. `statistique_modele` est peuplée par simple agrégation
des versions déjà analysées, pas par le moteur de rejeu complet décrit en L031.7
§4 (comparer des versions du modèle sur un historique identique) — non construit
dans cette tranche.
"""

from __future__ import annotations

from src.repositories.statistique_repository import StatistiqueRepository


class StatistiqueService:
    def __init__(self, statistique_repository: StatistiqueRepository) -> None:
        self._repo = statistique_repository

    def calculer_toutes(self) -> dict[str, int]:
        """Calcule et persiste une nouvelle ligne pour chacune des 6 tables
        statistiques (jamais de mise à jour, cf. L030.4 §10). Retourne le nombre
        de lignes créées par table (0 ou 1 pour `globale`, N pour les autres)."""
        resume: dict[str, int] = {}

        self._repo.create_globale(self._repo.calculer_globale())
        resume["globale"] = 1

        resume["scores"] = sum(1 for s in self._repo.calculer_scores() if self._repo.create_score(s))

        resume["hippodromes"] = sum(1 for s in self._repo.calculer_hippodromes() if self._repo.create_hippodrome(s))

        resume["disciplines"] = sum(1 for s in self._repo.calculer_disciplines() if self._repo.create_discipline(s))

        resume["paris"] = sum(1 for s in self._repo.calculer_paris() if self._repo.create_pari_stat(s))

        resume["modeles"] = sum(1 for s in self._repo.calculer_modeles() if self._repo.create_modele(s))

        return resume
