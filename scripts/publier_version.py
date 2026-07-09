"""Publie une ligne dans la table `version` — cf. L018 §10 (« consulter les
versions »). Geste de déploiement (comme `scripts/creer_utilisateur.py`), pas
une action d'exploitation quotidienne : pas de route API d'écriture.

Usage :

    python scripts/publier_version.py --version 0.2.0 --commentaire "..."
"""

from __future__ import annotations

import argparse
import subprocess
import sys

from src.database.connection import session
from src.models.technique import Version
from src.repositories.version_repository import VersionRepository


def _git(*args: str) -> str | None:
    try:
        return subprocess.run(
            ["git", *args], check=True, capture_output=True, text=True
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, help="Ex. 0.2.0")
    parser.add_argument("--commentaire", default=None)
    args = parser.parse_args()

    commit_git = _git("rev-parse", "HEAD")
    branche = _git("rev-parse", "--abbrev-ref", "HEAD")

    with session() as conn:
        ligne = VersionRepository(conn).creer(
            Version(version=args.version, commit_git=commit_git, branche=branche, commentaire=args.commentaire)
        )

    print(f"Version publiée : {ligne.version} (commit {ligne.commit_git}, branche {ligne.branche})")
    return 0


if __name__ == "__main__":
    sys.exit(run())
