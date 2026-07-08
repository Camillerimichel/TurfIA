"""Fonctions pures d'extraction du HTML Zone-Turf — cf. L006 §4.2 (pureté
fonctionnelle) : aucun accès réseau ici, tout est fourni en paramètre (page HTML
déjà récupérée par `ZoneTurfClient`) et retourné explicitement.

Périmètre volontaire (cf. plan de collecte, 2026-07-08) : seule la ligne
« Synthèse Quinté de la presse » constitue un véritable consensus multi-titres
(cf. L031.2 §Presse) — la sélection maison Zone-Turf (première ligne du tableau,
logo du site) est mono-source et hors périmètre, même principe déjà appliqué au
tri des blocs Canalturf (cf. src/collecte/canalturf/mappers.py).
"""

from __future__ import annotations

import re

from src.core.exceptions import ImportationError

_MOTIF_REUNION_COURSE = re.compile(r"R(\d+)\s*C(\d+)")
_MOTIF_LIGNE_SYNTHESE = re.compile(r"<tr>(?:(?!</tr>).)*Synthèse Quinté de la presse(?:(?!</tr>).)*</tr>", re.S)
_MOTIF_NUMERO_PARTANT = re.compile(r'<td class="tc">(\d+)</td>')


def extraire_numero_reunion_course(html_quinte: str) -> tuple[int, int] | None:
    """Extrait `(numéro de réunion, numéro de course)` du repère `R{n} C{n}` de la
    page, ou `None` si absent (aucun Quinté+ programmé aujourd'hui, état légitime)."""
    match = _MOTIF_REUNION_COURSE.search(html_quinte)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def extraire_synthese_presse(html_quinte: str) -> list[int] | None:
    """Retourne la liste ordonnée des numéros de partants de la ligne « Synthèse
    Quinté de la presse », ou `None` si cette ligne est absente."""
    ligne = _MOTIF_LIGNE_SYNTHESE.search(html_quinte)
    if not ligne:
        return None
    numeros = [int(n) for n in _MOTIF_NUMERO_PARTANT.findall(ligne.group(0))]
    if not numeros:
        raise ImportationError("Ligne « Synthèse Quinté de la presse » trouvée mais aucun numéro de partant extrait.")
    return numeros
