"""Fonctions pures de traduction du format PMU vers le vocabulaire TurfIA — cf.
L006 §4.2 (pureté fonctionnelle) : aucune donnée n'est lue ou écrite ici, tout est
fourni en paramètre et retourné explicitement.

Toute valeur non reconnue lève `ImportationError` plutôt que d'être devinée
silencieusement (cf. L009 §2.1, « ne fais aucune hypothèse »).
"""

from __future__ import annotations

from datetime import datetime

from src.core.exceptions import ImportationError

# Vérifié manuellement le 2026-07-07 sur le programme du jour (cf. plan de collecte) ;
# code PMU -> libellé TurfIA (cf. L030.1 seed des référentiels).
DISCIPLINES_PMU: dict[str, str] = {
    "PLAT": "Plat",
    "ATTELE": "Trot Attelé",
    "MONTE": "Trot Monté",
    "HAIES": "Haies",
    "STEEPLE-CHASE": "Steeple",
    "CROSS": "Cross",
}

# Idem, uniquement les codes réellement observés ; complété au fur et à mesure.
SURFACES_PMU: dict[str, str] = {
    "HERBE": "Gazon",
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
