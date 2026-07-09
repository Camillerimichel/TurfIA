"""Sauvegarde de la base PostgreSQL via `pg_dump` — cf. L018 §10 (« vérifier les
sauvegardes »), L038. Usage :

    python scripts/sauvegarder_base.py

Déclenchement manuel uniquement (pas de scheduler OS dans cette tranche, cf.
décision déjà actée sur les automatisations planifiées) ; `executer_sauvegarde`
est réutilisée telle quelle par `POST /administration/sauvegardes` (cf. L033
ADR-002, jamais de logique dupliquée).
"""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from src.core.config import get_settings
from src.database.connection import session
from src.repositories.tache_repository import TacheRepository


def executer_sauvegarde(database_url: str, repertoire: str) -> tuple[Path, int]:
    """Exécute `pg_dump --format=custom` vers `repertoire`, retourne (chemin,
    taille_octets). Lève `subprocess.CalledProcessError` si `pg_dump` échoue.

    Le mot de passe est transmis via la variable d'environnement `PGPASSWORD`
    (jamais en argument de ligne de commande, pour ne pas apparaître dans la
    liste des processus, cf. L021 §5.1 — un identifiant est une donnée sensible).
    """
    dossier = Path(repertoire)
    dossier.mkdir(parents=True, exist_ok=True)
    horodatage = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    chemin = dossier / f"turfia_{horodatage}.dump"

    url = urlparse(database_url)
    env = {**os.environ, "PGPASSWORD": url.password or ""}
    subprocess.run(
        [
            "pg_dump",
            "--format=custom",
            "--file",
            str(chemin),
            "--host",
            url.hostname or "localhost",
            "--port",
            str(url.port or 5432),
            "--username",
            url.username or "",
            (url.path or "").lstrip("/"),
        ],
        check=True,
        capture_output=True,
        env=env,
    )
    return chemin, chemin.stat().st_size


def run() -> int:
    settings = get_settings()
    with session() as conn:
        tache_repo = TacheRepository(conn)
        tache = tache_repo.demarrer("sauvegarde_base", categorie="sauvegarde")
        try:
            chemin, taille = executer_sauvegarde(settings.database_url, settings.chemin_sauvegardes)
        except subprocess.CalledProcessError as exc:
            tache_repo.terminer(tache.id, "echec", commentaire=exc.stderr.decode(errors="replace")[:2000])
            print(f"Échec de la sauvegarde : {exc}")
            return 1
        tache_repo.terminer(tache.id, "succes", commentaire=f"{chemin} ({taille} octets)")
    print(f"Sauvegarde créée : {chemin} ({taille} octets)")
    return 0


if __name__ == "__main__":
    sys.exit(run())
