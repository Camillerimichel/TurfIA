"""Fonctions pures d'extraction du HTML Canalturf — cf. L006 §4.2 (pureté
fonctionnelle) : aucun accès réseau ici, tout est fourni en paramètre (page HTML
déjà récupérée par `CanalturfClient`) et retourné explicitement.

Périmètre volontaire (cf. plan de collecte, 2026-07-07) : seul le bloc « La
sélection de la presse » (id="tab-prono-pr") constitue un véritable consensus
multi-journaux (cf. L031.2 §Presse : « consensus, nombre de citations »). Vérifié
réel : ce bloc n'existe que sur la page de la course Quinté+ du jour, jamais sur
les autres courses — les sélections mono-source de la même page (BASE, ZEturf.fr,
etc.) sont hors périmètre.
"""

from __future__ import annotations

import re

from src.core.exceptions import ImportationError

_MOTIF_URL_QUINTE = re.compile(
    r'href="(https://www\.canalturf\.com/pronostics-PMU/\d{4}-\d{2}-\d{2}/[^"]+\.html)"'
)
_MOTIF_CAPTION = re.compile(r"<caption[^>]*>([^<]*)</caption>")
_MOTIF_REUNION_COURSE = re.compile(r"R(\d+)C(\d+)")
_MOTIF_NUMERO_PARTANT = re.compile(r"<td>(\d+)</td>")


def extraire_url_quinte_du_jour(html_quinte: str) -> str | None:
    """Retourne l'URL de la page de pronostics du Quinté+ du jour, ou `None` si
    absente (un jour sans Quinté+ est un état légitime, pas une erreur)."""
    match = _MOTIF_URL_QUINTE.search(html_quinte)
    return match.group(1) if match else None


def extraire_numero_reunion_course(html_course: str) -> tuple[int, int]:
    """Extrait `(numéro de réunion, numéro de course)` du caption `R{n}C{n}` de
    la page de pronostics (ex. « R1C8 »). Lève `ImportationError` si la page ne
    présente pas la structure attendue, plutôt que de deviner."""
    caption = _MOTIF_CAPTION.search(html_course)
    if not caption:
        raise ImportationError("Caption Canalturf introuvable (structure de page inattendue).")
    numeros = _MOTIF_REUNION_COURSE.search(caption.group(1))
    if not numeros:
        raise ImportationError(f"Format 'R{{réunion}}C{{course}}' introuvable dans le caption : {caption.group(1)!r}")
    return int(numeros.group(1)), int(numeros.group(2))


def extraire_consensus_presse(html_course: str) -> list[int] | None:
    """Retourne la liste ordonnée des numéros de partants du bloc « La sélection
    de la presse », ou `None` si ce bloc est absent (course non-Quinté+)."""
    debut_bloc = html_course.find('id="tab-prono-pr"')
    if debut_bloc == -1:
        return None
    debut_tbody = html_course.find("<tbody>", debut_bloc)
    fin_tbody = html_course.find("</tbody>", debut_tbody) if debut_tbody != -1 else -1
    if debut_tbody == -1 or fin_tbody == -1:
        raise ImportationError("Bloc presse Canalturf trouvé mais sans tableau exploitable.")
    numeros = [int(n) for n in _MOTIF_NUMERO_PARTANT.findall(html_course[debut_tbody:fin_tbody])]
    if not numeros:
        raise ImportationError("Bloc presse Canalturf trouvé mais aucun numéro de partant extrait.")
    return numeros
