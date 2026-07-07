"""Client HTTP pour l'API interne du PMU (niveau 1 données officielles, niveau 2
cotes marché — cf. src/collecte/registre.py).

Usage non officiel d'une API interne (non documentée publiquement pour usage tiers,
utilisée par le site/l'application PMU eux-mêmes), vérifiée manuellement le
2026-07-07 (cf. plan de collecte). Respect explicite : délai entre appels successifs,
en-tête User-Agent identifiant l'origine, aucune authentification contournée, aucune
donnée personnelle collectée (uniquement des données de courses publiques).
"""

from __future__ import annotations

import time
from datetime import date

import httpx

from src.core.exceptions import ImportationError

BASE_URL = "https://online.turfinfo.api.pmu.fr/rest/client/61"
USER_AGENT = "TurfIA/0.1 (collecte de programme hippique, usage personnel non commercial)"
DELAI_ENTRE_APPELS_SECONDES = 0.3


class PMUClient:
    def __init__(self, delai_entre_appels: float = DELAI_ENTRE_APPELS_SECONDES, timeout: float = 10.0) -> None:
        self._delai = delai_entre_appels
        self._client = httpx.Client(headers={"User-Agent": USER_AGENT, "Accept": "application/json"}, timeout=timeout)
        self._dernier_appel: float | None = None

    def __enter__(self) -> "PMUClient":
        return self

    def __exit__(self, *_args: object) -> None:
        self.fermer()

    def fermer(self) -> None:
        self._client.close()

    def _patienter(self) -> None:
        if self._dernier_appel is not None:
            ecoule = time.monotonic() - self._dernier_appel
            if ecoule < self._delai:
                time.sleep(self._delai - ecoule)
        self._dernier_appel = time.monotonic()

    def _get(self, url: str) -> dict:
        self._patienter()
        try:
            reponse = self._client.get(url)
            reponse.raise_for_status()
        except httpx.HTTPError as exc:
            raise ImportationError(f"Échec de la requête vers l'API PMU ({url}) : {exc}") from exc
        try:
            return reponse.json()
        except ValueError as exc:
            raise ImportationError(f"Réponse PMU non JSON ({url}).") from exc

    def recuperer_programme(self, jour: date) -> dict:
        return self._get(f"{BASE_URL}/programme/{jour:%d%m%Y}")

    def recuperer_participants(self, jour: date, num_reunion: int, num_course: int) -> dict:
        return self._get(f"{BASE_URL}/programme/{jour:%d%m%Y}/R{num_reunion}/C{num_course}/participants")
