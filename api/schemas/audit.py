"""Schéma du domaine Audit — cf. L021 §13, L030.5.

Lecture seule : la table `audit` n'est alimentée que par les routes
d'écriture elles-mêmes (cf. `api/routes/courses.py`, `api/routes/analyses.py`,
`AuthService`), jamais directement via cette route.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    utilisateur_id: int | None = None
    date_action: datetime
    action: str
    objet: str | None = None
    ancien_etat: str | None = None
    nouvel_etat: str | None = None
