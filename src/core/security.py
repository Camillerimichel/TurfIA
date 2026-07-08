"""Primitives de sécurité — hachage des mots de passe et des jetons de session
(cf. L021 §3.2, §3.3, §5.1). Fonctions pures, aucun accès à la base ou au réseau.
"""

from __future__ import annotations

import hashlib
import secrets

import bcrypt

TAILLE_JETON_OCTETS = 32


def hacher_mot_de_passe(mot_de_passe: str) -> str:
    """Hache un mot de passe en clair (bcrypt, jamais stocké/affiché en clair,
    cf. L021 §3.2)."""
    return bcrypt.hashpw(mot_de_passe.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verifier_mot_de_passe(mot_de_passe: str, hache: str) -> bool:
    return bcrypt.checkpw(mot_de_passe.encode("utf-8"), hache.encode("utf-8"))


def generer_jeton() -> str:
    """Jeton de session opaque (aléatoire, non prévisible) — cf. L021 §3.3."""
    return secrets.token_urlsafe(TAILLE_JETON_OCTETS)


def hacher_jeton(jeton: str) -> str:
    """Seul ce hash est stocké en base : un jeton en clair est une donnée sensible
    (cf. L021 §5.1) qu'une simple lecture de la table `session` ne doit jamais
    pouvoir exploiter."""
    return hashlib.sha256(jeton.encode("utf-8")).hexdigest()
