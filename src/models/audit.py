"""Modèle de la table `audit` — cf. L021 §13, L030.5.

Traçabilité des opérations sensibles : jamais mise à jour en place, une
nouvelle ligne par action (cf. L030.5 §11, tables techniques historisées).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Audit:
    action: str
    id: int | None = None
    utilisateur_id: int | None = None
    date_action: datetime | None = None
    objet: str | None = None
    ancien_etat: str | None = None
    nouvel_etat: str | None = None
