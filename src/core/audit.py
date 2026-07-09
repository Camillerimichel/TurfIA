"""Sérialisation de l'état pour la table `audit` — cf. L021 §13, L030.5.

Fonction pure (cf. L006 §4.2) : aucun accès réseau ou base ici. Aucun des
modèles sérialisés via cette fonction (Reunion/Course/Cheval/Jockey/
Entraineur/Partant/Resultat/Cote/Analyse) ne porte de champ sensible —
contrairement à Utilisateur.mot_de_passe/Session.jeton, jamais audités.
"""

from __future__ import annotations

import dataclasses
import json


def serialiser_etat(obj: object | None) -> str | None:
    if obj is None:
        return None
    return json.dumps(dataclasses.asdict(obj), default=str, ensure_ascii=False)
