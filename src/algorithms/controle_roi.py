"""Calcul du ROI réel a posteriori (cf. L011 §8.7 table `controle_roi`, L030.4) —
fonctions pures (cf. L006 §4.2), aucun accès réseau ou base ici.

Couvre les 6 types de pari que `AnalyseService`/`construire_paris` peuvent
construire (cf. L031.6 §5) : Simple Gagnant/Placé, Couplé Gagnant/Placé,
2 sur 4, Quinté Flexi. Depuis le 2026-07-13 (retour utilisateur, structure de
paris spécifique aux courses Quinté+), les 4 derniers ne sont en réalité
construits que pour une course Quinté+ (`quinte=True`, cf. `construire_paris`) —
une analyse de course ordinaire ne produit plus que Simple Gagnant/Placé,
seuls types réellement offerts par le PMU sur toute course.

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


def calculer_gains_quinte_flexi(
    mise_par_combinaison: float,
    sous_combinaisons: list[frozenset[str]],
    numeros_arrivee: frozenset[str],
    dividende_desordre: float,
    dividendes_bonus4: dict[frozenset[str], float],
    dividendes_bonus3: dict[frozenset[str], float],
    rembourse: bool,
) -> float:
    """Gains réels d'un pari Quinté Flexi, comparé au rapport officiel PMU (cf.
    `src.collecte.pmu.mappers.extraire_rapport_quinte`). Le Flexi joue
    automatiquement toutes les combinaisons de 5 chevaux parmi les chevaux
    sélectionnés (`sous_combinaisons`, cf. `construire_paris`) : chacune est
    évaluée indépendamment (une même sélection peut gagner sur plusieurs
    combinaisons à la fois, notamment en Bonus 4sur5) et les gains sont sommés.

    - Pari remboursé : chaque combinaison est remboursée à parité.
    - Combinaison égale aux 5 numéros d'arrivée : gains = mise par combinaison ×
      dividende Désordre (jamais Ordre, cf. `RapportQuinte`).
    - Sinon, si 4 de ses numéros correspondent à un quadruple Bonus 4sur5 :
      gains = mise par combinaison × ce dividende.
    - Sinon, si 3 de ses numéros correspondent à un triplet Bonus 3 : idem.
    - Sinon : combinaison perdante.
    """
    if rembourse:
        return mise_par_combinaison * len(sous_combinaisons)

    gains = 0.0
    for combinaison in sous_combinaisons:
        if combinaison == numeros_arrivee:
            gains += mise_par_combinaison * dividende_desordre
            continue
        dividende_bonus4 = next((div for combo, div in dividendes_bonus4.items() if combo <= combinaison), None)
        if dividende_bonus4 is not None:
            gains += mise_par_combinaison * dividende_bonus4
            continue
        dividende_bonus3 = next((div for combo, div in dividendes_bonus3.items() if combo <= combinaison), None)
        if dividende_bonus3 is not None:
            gains += mise_par_combinaison * dividende_bonus3
    return gains
