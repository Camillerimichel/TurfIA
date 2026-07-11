"""Fonctions pures de traduction du format PMU vers le vocabulaire TurfIA — cf.
L006 §4.2 (pureté fonctionnelle) : aucune donnée n'est lue ou écrite ici, tout est
fourni en paramètre et retourné explicitement.

Toute valeur non reconnue lève `ImportationError` plutôt que d'être devinée
silencieusement (cf. L009 §2.1, « ne fais aucune hypothèse »).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.core.exceptions import ImportationError

# Vérifié manuellement le 2026-07-07 sur le programme du jour (cf. plan de collecte) ;
# code PMU -> libellé TurfIA (cf. L030.1 seed des référentiels). "HAIE"/"STEEPLECHASE"
# (sans le S/le tiret) observés réellement le 2026-07-10 sur une réunion différente —
# PMU n'est pas toujours cohérent sur l'orthographe exacte du code, complété au fur
# et à mesure plutôt que deviné.
DISCIPLINES_PMU: dict[str, str] = {
    "PLAT": "Plat",
    "ATTELE": "Trot Attelé",
    "MONTE": "Trot Monté",
    "HAIES": "Haies",
    "HAIE": "Haies",
    "STEEPLE-CHASE": "Steeple",
    "STEEPLECHASE": "Steeple",
    "CROSS": "Cross",
}

# Idem, uniquement les codes réellement observés ; complété au fur et à mesure.
# "GAZON" observé réellement le 2026-07-11 (réunion R8) en plus de "HERBE" —
# même incohérence PMU que HAIE/HAIES ou STEEPLE-CHASE/STEEPLECHASE ci-dessus.
# "DIRT"/"SABLE" ajoutés le 2026-07-11 à la demande explicite de l'utilisateur,
# par anticipation (pas encore observés littéralement) pour les réunions
# internationales sur piste en terre/sable (ex. hippodromes américains) — la
# réunion R8 du 2026-07-11 elle-même envoyait "GAZON" pour des courses
# pourtant "(DIRT)" dans leur nom (anomalie PMU documentée dans
# PROJECT_STATE.md, non corrigée ici : le code PMU reçu reste "GAZON" pour
# ces 5 courses précises, ce mapping ne s'applique qu'aux futures courses où
# PMU envoie réellement "DIRT"/"SABLE").
SURFACES_PMU: dict[str, str] = {
    "HERBE": "Gazon",
    "GAZON": "Gazon",
    "DIRT": "Dirt",
    "SABLE": "Sable",
}

# Vérifié réellement le 2026-07-08 (course Quinté+ R1C8, programme du jour) :
# TurfIA type_pari (cf. TYPES_PARI) -> code PMU réel (champ `typePari` des rapports
# définitifs). Couplé Gagnant/Placé, 2 sur 4 et Quinté Flexi ne sont exposés par
# PMU que sur les courses Quinté+ (une course ordinaire propose `COUPLE_ORDRE`,
# à ordre exigé, pas le même pari) — limite documentée, cf. PROJECT_STATE.md.
TYPES_PARI_PMU: dict[str, str] = {
    "Simple Gagnant": "SIMPLE_GAGNANT",
    "Simple Placé": "SIMPLE_PLACE",
    "Couplé Gagnant": "COUPLE_GAGNANT",
    "Couplé Placé": "COUPLE_PLACE",
    "2 sur 4": "DEUX_SUR_QUATRE",
    "Quinté Flexi": "QUINTE_PLUS",
}


def mapper_discipline_code(code_pmu: str) -> str:
    try:
        return DISCIPLINES_PMU[code_pmu]
    except KeyError as exc:
        raise ImportationError(
            f"Code discipline PMU inconnu : '{code_pmu}'. Ajouter une correspondance dans DISCIPLINES_PMU."
        ) from exc


def mapper_surface_code(code_pmu: str | None) -> str | None:
    if code_pmu is None:
        return None
    try:
        return SURFACES_PMU[code_pmu]
    except KeyError as exc:
        raise ImportationError(
            f"Code surface PMU inconnu : '{code_pmu}'. Ajouter une correspondance dans SURFACES_PMU."
        ) from exc


def extraire_etat_piste_libelle(course_brute: dict) -> str | None:
    """Le pénétromètre PMU fournit déjà un libellé en clair (ex. « Bon »), directement
    compatible avec `etat_piste.libelle` (cf. L030.1) — aucune table de correspondance
    n'est nécessaire, contrairement à la discipline ou la surface (codes PMU).
    """
    penetrometre = course_brute.get("penetrometre")
    if not penetrometre:
        return None
    return penetrometre.get("intitule")


def horodatage_depuis_epoch_ms(valeur_ms: int | None) -> datetime | None:
    if valeur_ms is None:
        return None
    return datetime.fromtimestamp(valeur_ms / 1000)


def extraire_cote_directe(participant_brut: dict) -> float | None:
    """Cote « simple gagnant » directe (cf. L030.2 table `cote`, niveau 2 marché)."""
    rapport = participant_brut.get("dernierRapportDirect")
    if not rapport or rapport.get("typePari") != "SIMPLE_GAGNANT":
        return None
    return rapport.get("rapport")


def extraire_classement(participant_brut: dict) -> int | None:
    """Rang d'arrivée officiel si la course est arrivée, sinon None (cf. L030.2 table
    `resultat`).
    """
    return participant_brut.get("ordreArrivee")


def _trouver_entree_rapport(rapports_bruts: list[dict], type_pari_pmu: str) -> dict:
    entree = next((r for r in rapports_bruts if r.get("typePari") == type_pari_pmu), None)
    if entree is None:
        raise ImportationError(f"Aucun rapport '{type_pari_pmu}' trouvé dans les rapports définitifs PMU.")
    return entree


def extraire_rapport_simple(rapports_bruts: list[dict], type_pari_pmu: str) -> tuple[dict[str, float], bool]:
    """Rapport officiel réel « Simple Gagnant » ou « Simple Placé » (cf. L011 §8.7
    table `controle_roi`) : `({numéro_gagnant: dividende_pour_un_euro_en_euros},
    rembourse)`. Simple Placé peut avoir plusieurs numéros gagnants (un par cheval
    placé), chacun avec son propre dividende — contrairement à Simple Gagnant qui
    n'en a qu'un seul, d'où un dict plutôt qu'une valeur unique.

    `dividendePourUnEuro` est fourni par PMU en centimes (ex. 140 -> 1,40 € par
    € misé) ; converti ici en euros pour que l'appelant fasse
    `mise * dividende_pour_un_euro` directement.

    Lève `ImportationError` si l'entrée `type_pari_pmu` est absente — structurellement
    inattendu une fois `rapportsDefinitifsDisponibles` vrai côté PMU.
    """
    entree = _trouver_entree_rapport(rapports_bruts, type_pari_pmu)
    if bool(entree.get("rembourse", False)):
        return {}, True

    rapports = entree.get("rapports") or []
    dividendes = {
        r["combinaison"]: r["dividendePourUnEuro"] / 100
        for r in rapports
        if "combinaison" in r and "dividendePourUnEuro" in r
    }
    if not dividendes:
        raise ImportationError(f"Rapport '{type_pari_pmu}' trouvé mais sans combinaison/dividende exploitable.")
    return dividendes, False


def extraire_rapport_couple(rapports_bruts: list[dict], type_pari_pmu: str) -> tuple[dict[frozenset[str], float], bool]:
    """Rapport officiel réel « Couplé Gagnant » ou « Couplé Placé » (cf. L011 §8.7) :
    `({frozenset({numéro1, numéro2}): dividende_pour_un_euro_en_euros, ...}, rembourse)`.
    Couplé Placé a plusieurs paires gagnantes (une par paire de chevaux placés parmi
    l'arrivée), chacune avec son propre dividende. Les entrées non-partant
    (combinaison contenant "NP", ex. "5-NP") sont ignorées : un numéro réel de
    partant ne peut jamais correspondre à "NP" (cf. limite documentée, remboursement
    non-partant non modélisé).

    Le couplage est par nature non ordonné (Couplé Gagnant : arrivés 1er+2e dans
    n'importe quel ordre, distinct du pari PMU « Couplé Ordre » qui exige l'ordre) —
    `frozenset` reflète cette absence d'ordre.
    """
    entree = _trouver_entree_rapport(rapports_bruts, type_pari_pmu)
    if bool(entree.get("rembourse", False)):
        return {}, True

    rapports = entree.get("rapports") or []
    dividendes: dict[frozenset[str], float] = {}
    for r in rapports:
        combinaison = r.get("combinaison")
        if not combinaison or "dividendePourUnEuro" not in r:
            continue
        numeros = combinaison.split("-")
        if "NP" in numeros:
            continue
        dividendes[frozenset(numeros)] = r["dividendePourUnEuro"] / 100
    if not dividendes:
        raise ImportationError(f"Rapport '{type_pari_pmu}' trouvé mais sans combinaison/dividende exploitable.")
    return dividendes, False


def extraire_rapport_deux_sur_quatre(rapports_bruts: list[dict]) -> tuple[frozenset[str], float, bool]:
    """Rapport officiel réel « 2 sur 4 » (cf. L011 §8.7) :
    `(numéros_des_4_premiers_arrivés, dividende_pour_un_euro_en_euros, rembourse)`.

    PMU liste les 6 paires gagnantes (toutes les combinaisons possibles parmi les 4
    premiers arrivés, cf. vérification réelle du 2026-07-08) avec un dividende
    identique pour chacune : les 4 premiers arrivés sont reconstruits par union de
    ces paires, et le contrôle réel se fait par intersection (« au moins 2 des 4
    chevaux joués parmi les 4 premiers arrivés »), pas par égalité de paire.
    """
    entree = _trouver_entree_rapport(rapports_bruts, "DEUX_SUR_QUATRE")
    if bool(entree.get("rembourse", False)):
        return frozenset(), 0.0, True

    rapports = entree.get("rapports") or []
    numeros_arrivee: set[str] = set()
    dividende: float | None = None
    for r in rapports:
        combinaison = r.get("combinaison")
        if not combinaison or "dividendePourUnEuro" not in r:
            continue
        numeros = combinaison.split("-")
        if "NP" in numeros:
            continue
        numeros_arrivee.update(numeros)
        if dividende is None:
            dividende = r["dividendePourUnEuro"] / 100
    if not numeros_arrivee or dividende is None:
        raise ImportationError("Rapport 'DEUX_SUR_QUATRE' trouvé mais sans combinaison/dividende exploitable.")
    return frozenset(numeros_arrivee), dividende, False


@dataclass(frozen=True)
class RapportQuinte:
    """Rapport officiel réel « Quinté+ » (cf. L011 §8.7), tel qu'exploité par
    Quinté Flexi — jamais l'entrée « Ordre » (nos tickets ne committent jamais
    un ordre d'arrivée, cf. `src.algorithms.controle_roi.calculer_gains_quinte_flexi`).
    """

    numeros_arrivee: frozenset[str]
    dividende_desordre: float
    dividendes_bonus4: dict[frozenset[str], float]
    dividendes_bonus3: dict[frozenset[str], float]
    rembourse: bool


def extraire_rapport_quinte(rapports_bruts: list[dict]) -> RapportQuinte:
    """Extrait le rapport « Quinté+ Désordre » (1 combinaison gagnante de 5
    numéros), « Bonus 4sur5 » et « Bonus 3 » (une ou plusieurs combinaisons
    partielles chacun, dividende propre à chacune — vérifié réellement le
    2026-07-08, R1C8 du 07/07/2026 : Bonus 4sur5 en compte 5 (tous les
    quadruples possibles parmi les 5 arrivants), Bonus 3 n'en compte qu'une
    seule dans l'échantillon réel — aucune hypothèse n'est faite ici sur leur
    nombre, seulement sur ce qui est réellement listé).
    """
    entree = _trouver_entree_rapport(rapports_bruts, "QUINTE_PLUS")
    if bool(entree.get("rembourse", False)):
        return RapportQuinte(frozenset(), 0.0, {}, {}, True)

    numeros_arrivee: frozenset[str] = frozenset()
    dividende_desordre = 0.0
    dividendes_bonus4: dict[frozenset[str], float] = {}
    dividendes_bonus3: dict[frozenset[str], float] = {}

    for r in entree.get("rapports") or []:
        combinaison = r.get("combinaison")
        if not combinaison or "dividendePourUnEuro" not in r:
            continue
        numeros = combinaison.split("-")
        if "NP" in numeros:
            continue
        libelle = r.get("libelle", "")
        dividende = r["dividendePourUnEuro"] / 100
        if "Désordre" in libelle:
            numeros_arrivee = frozenset(numeros)
            dividende_desordre = dividende
        elif libelle.startswith("Bonus 4"):
            dividendes_bonus4[frozenset(numeros)] = dividende
        elif libelle.startswith("Bonus 3"):
            dividendes_bonus3[frozenset(numeros)] = dividende

    if not numeros_arrivee:
        raise ImportationError("Rapport 'QUINTE_PLUS' trouvé mais sans combinaison Désordre exploitable.")
    return RapportQuinte(numeros_arrivee, dividende_desordre, dividendes_bonus4, dividendes_bonus3, False)
