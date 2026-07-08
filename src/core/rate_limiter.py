"""Limitation de débit en mémoire pour les endpoints sensibles — cf. L021 §7.2.1.

Fenêtre glissante par clé (ex. login ou adresse IP), un seul processus : ne
distribue pas l'état entre plusieurs workers/instances (cf. limite documentée dans
PROJECT_STATE.md, même logique que les autres constructions "acceptables pour le
volume actuel" déjà actées ailleurs dans le projet).
"""

from __future__ import annotations

import time
from collections import defaultdict


class LimiteurDebit:
    def __init__(self, max_tentatives: int, fenetre_secondes: float) -> None:
        self._max_tentatives = max_tentatives
        self._fenetre_secondes = fenetre_secondes
        self._tentatives: dict[str, list[float]] = defaultdict(list)

    def autoriser(self, cle: str) -> bool:
        """Enregistre une tentative pour `cle` et retourne False si la limite est
        dépassée sur la fenêtre glissante."""
        maintenant = time.monotonic()
        seuil = maintenant - self._fenetre_secondes
        historique = [instant for instant in self._tentatives[cle] if instant > seuil]
        historique.append(maintenant)
        self._tentatives[cle] = historique
        return len(historique) <= self._max_tentatives
