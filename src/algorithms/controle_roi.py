"""Calcul du ROI réel a posteriori (cf. L011 §8.7 table `controle_roi`, L030.4) —
fonctions pures (cf. L006 §4.2), aucun accès réseau ou base ici.

Couvre les 5 types de pari construits par `AnalyseService` (cf. L031.6 §5) :
Simple Gagnant/Placé, Couplé Gagnant/Placé, 2 sur 4. Quinté Flexi est
volontairement hors périmètre (cf. plan, complexité disproportionnée).

Aucune de ces fonctions ne modélise le remboursement réglementaire PMU
spécifique à un partant devenu non-partant après l'analyse (règles pari-mutuel
non triviales, non vérifiées) : un tel cas est simplement traité comme perdant
(limite documentée, cf. PROJECT_STATE.md).
"""

from __future__ import annotations


def calculer_gains_simple(
    mise: float, numero_joue: str, dividendes_gagnants: dict[str, float], rembourse: bool
) -> float:
    """Gains réels d'un pari Simple Gagnant ou Simple Placé, comparé au rapport
    officiel PMU (cf. `src.collecte.pmu.mappers.extraire_rapport_simple`).

    - Pari remboursé (course annulée ou assimilée côté PMU) : la mise est rendue
      à parité, pas de gain ni de perte.
    - Numéro joué présent parmi les numéros gagnants : gains = mise × son
      dividende propre (Simple Placé a un dividende différent par cheval placé).
    - Sinon : pari perdant, gains nuls.
    """
    if rembourse:
        return mise
    if numero_joue in dividendes_gagnants:
        return mise * dividendes_gagnants[numero_joue]
    return 0.0


def calculer_gains_couple(
    mise: float, numeros_joues: frozenset[str], dividendes_gagnants: dict[frozenset[str], float], rembourse: bool
) -> float:
    """Gains réels d'un pari Couplé Gagnant ou Couplé Placé, comparé au rapport
    officiel PMU (cf. `src.collecte.pmu.mappers.extraire_rapport_couple`).

    - Pari remboursé : la mise est rendue à parité.
    - La paire jouée (ordre indifférent) correspond à une des paires gagnantes :
      gains = mise × le dividende propre à cette paire (Couplé Placé a plusieurs
      paires gagnantes, chacune avec son propre dividende).
    - Sinon : pari perdant, gains nuls.
    """
    if rembourse:
        return mise
    if numeros_joues in dividendes_gagnants:
        return mise * dividendes_gagnants[numeros_joues]
    return 0.0


def calculer_gains_deux_sur_quatre(
    mise: float, numeros_joues: frozenset[str], numeros_arrivee: frozenset[str], dividende_pour_un_euro: float, rembourse: bool
) -> float:
    """Gains réels d'un pari 2 sur 4, comparé au rapport officiel PMU (cf.
    `src.collecte.pmu.mappers.extraire_rapport_deux_sur_quatre`).

    - Pari remboursé : la mise est rendue à parité.
    - Au moins 2 des 4 numéros joués sont parmi les 4 premiers arrivés : gains =
      mise × dividende (identique quelle que soit la paire effectivement en
      commun, cf. vérification réelle du 2026-07-08).
    - Sinon : pari perdant, gains nuls.
    """
    if rembourse:
        return mise
    if len(numeros_joues & numeros_arrivee) >= 2:
        return mise * dividende_pour_un_euro
    return 0.0
