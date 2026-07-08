"""Calcul du ROI réel a posteriori (cf. L011 §8.7 table `controle_roi`, L030.4) —
fonction pure (cf. L006 §4.2), aucun accès réseau ou base ici.

Périmètre volontaire de cette tranche : `AnalyseService` ne génère aujourd'hui
qu'un seul type de pari, « Simple Gagnant » (cf. src/services/analyse_service.py),
donc seul ce type est contrôlé contre le rapport officiel réel (cf.
src/collecte/pmu/mappers.py, `extraire_rapport_simple_gagnant`).
"""

from __future__ import annotations


def calculer_gains_simple_gagnant(
    mise: float, numero_joue: str, combinaison_gagnante: str, dividende_pour_un_euro: float, rembourse: bool
) -> float:
    """Gains réels d'un pari Simple Gagnant, comparé au rapport officiel PMU.

    - Pari remboursé (course annulée ou assimilée côté PMU) : la mise est rendue
      à parité, pas de gain ni de perte.
    - Numéro joué = combinaison gagnante : gains = mise × dividende (déjà exprimé
      en euros par euro misé, cf. `extraire_rapport_simple_gagnant`).
    - Sinon : pari perdant, gains nuls.

    Ne modélise pas le remboursement réglementaire PMU spécifique à un partant
    devenu non-partant après l'analyse (règles pari-mutuel non triviales, non
    vérifiées) : un tel cas est simplement traité comme perdant si son numéro ne
    correspond pas à la combinaison gagnante (limite documentée, cf. PROJECT_STATE.md).
    """
    if rembourse:
        return mise
    if numero_joue == combinaison_gagnante:
        return mise * dividende_pour_un_euro
    return 0.0
