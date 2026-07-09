"""Agrégation pure du moteur de rejeu/backtesting (cf. L031.7 §4) — fonction
pure (cf. L006 §4.2), aucun accès réseau ou base ici.

Ne fait qu'agréger des résultats de paris déjà contrôlés contre des rapports
PMU réels (cf. `ControleRoiService.calculer_gains_pari`, réutilisé tel quel par
`scripts/rejouer_versions.py`) — le rejeu ne réimplémente aucune logique de
calcul de gains, seulement la synthèse ROI/taux de réussite sur l'ensemble
rejoué, à la manière de `StatistiqueRepository.calculer_modeles` (même formule).
"""

from __future__ import annotations


def agreger_resultats_rejeu(
    resultats_paris: list[tuple[float, float, bool]],
) -> tuple[int, float | None, float | None]:
    """`resultats_paris` : une entrée `(mise, gains, valide)` par pari contrôlé
    sur l'ensemble de l'historique rejoué. Retourne `(nb_paris, roi,
    taux_reussite)` — `roi`/`taux_reussite` sont `None` si `resultats_paris` est
    vide (rien à diviser).
    """
    nb_paris = len(resultats_paris)
    if nb_paris == 0:
        return 0, None, None

    mise_totale = sum(mise for mise, _, _ in resultats_paris)
    gains_totaux = sum(gains for _, gains, _ in resultats_paris)
    nb_valides = sum(1 for _, _, valide in resultats_paris if valide)

    roi = ((gains_totaux - mise_totale) / mise_totale) * 100 if mise_totale else None
    taux_reussite = (nb_valides / nb_paris) * 100

    return nb_paris, roi, taux_reussite
