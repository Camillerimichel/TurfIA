"""Interface commune des adaptateurs de collecte — architecture multi-sources en
4 niveaux (données officielles, marché, consensus presse, base TurfIA propriétaire).

Un `Collecteur` est délibérément une interface structurelle (Protocol) et non une
classe abstraite : elle ne fait que documenter la forme attendue, sans imposer de
hiérarchie d'héritage à des sources aux modèles de données très différents (JSON
structuré pour PMU, HTML pour la presse, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Protocol


class Collecteur(Protocol):
    """Forme attendue d'un adaptateur de source de données hippiques."""

    def recuperer_programme(self, jour: date) -> Any:
        """Retourne le programme brut (réunions/courses) de la source pour `jour`."""
        ...

    def recuperer_participants(self, jour: date, ref_reunion: int, ref_course: int) -> Any:
        """Retourne les partants bruts d'une course donnée de la source."""
        ...


@dataclass(frozen=True)
class SourceInfo:
    """Déclaration d'une source connue (implémentée ou non) — cf. registre.py."""

    nom: str
    niveau: int
    role: str
    implementee: bool
    raison_si_non_implementee: str | None = None
