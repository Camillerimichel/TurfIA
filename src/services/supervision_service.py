"""Supervision — cf. L018 §10 (« contrôler la supervision »), L035.

Périmètre volontairement réduit par rapport à L035 (métriques CPU/mémoire/
disque avec agents et seuils d'alerte) : proportionné à un usage local
mono-utilisateur — connexion DB (ok/latence), espace disque disponible pour
les sauvegardes, échecs de tâches récents (`tache`), uptime du processus. Pas
de nouvelle dépendance (`psutil` écarté) : uniquement `shutil`/`time`/stdlib.
"""

from __future__ import annotations

import shutil
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import psycopg

from src.repositories.tache_repository import TacheRepository


@dataclass(frozen=True)
class EtatSupervision:
    base_de_donnees_ok: bool
    latence_db_ms: float | None
    espace_disque_disponible_octets: int
    taches_en_echec_24h: int
    demarrage_processus: datetime
    uptime_secondes: float


class SupervisionService:
    def __init__(
        self,
        database_url: str,
        chemin_sauvegardes: str,
        tache_repository: TacheRepository,
        demarrage_processus: datetime,
    ) -> None:
        self._database_url = database_url
        self._chemin_sauvegardes = chemin_sauvegardes
        self._taches = tache_repository
        self._demarrage = demarrage_processus

    def _ping_db(self) -> tuple[bool, float | None]:
        debut = time.monotonic()
        try:
            with psycopg.connect(self._database_url, connect_timeout=2) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    cur.fetchone()
            return True, (time.monotonic() - debut) * 1000
        except psycopg.Error:
            return False, None

    def etat(self) -> EtatSupervision:
        base_de_donnees_ok, latence_db_ms = self._ping_db()
        try:
            espace_disque = shutil.disk_usage(self._chemin_sauvegardes).free
        except FileNotFoundError:
            espace_disque = shutil.disk_usage(".").free

        maintenant = datetime.now(timezone.utc)
        return EtatSupervision(
            base_de_donnees_ok=base_de_donnees_ok,
            latence_db_ms=latence_db_ms,
            espace_disque_disponible_octets=espace_disque,
            taches_en_echec_24h=self._taches.compter_echecs_recents(maintenant - timedelta(hours=24)),
            demarrage_processus=self._demarrage,
            uptime_secondes=(maintenant - self._demarrage).total_seconds(),
        )
