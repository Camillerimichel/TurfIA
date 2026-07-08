"""Client HTTP pour Zone-Turf (niveau 3, consensus presse — cf.
src/collecte/registre.py).

Scraping HTML d'un site tiers public, vérifié manuellement le 2026-07-08 (cf.
plan de collecte) : robots.txt de zone-turf.fr autorise `User-agent: *` sur tout
le site sauf `/navi/`, `/async/`, `/abonnes/` (espace abonnés, non utilisé ici),
avec un `Crawl-delay: 10` explicite — repris tel quel ci-dessous. Aucune mention
`anthropic-ai`, contrairement à Paris-Turf.
"""

from __future__ import annotations

import time

import httpx

from src.core.exceptions import ImportationError

BASE_URL = "https://www.zone-turf.fr"
USER_AGENT = "TurfIA/0.1 (collecte de pronostics hippiques, usage personnel non commercial)"
DELAI_ENTRE_APPELS_SECONDES = 10.0  # cf. Crawl-delay du robots.txt du site


class ZoneTurfClient:
    def __init__(self, delai_entre_appels: float = DELAI_ENTRE_APPELS_SECONDES, timeout: float = 10.0) -> None:
        self._delai = delai_entre_appels
        self._client = httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=timeout)
        self._dernier_appel: float | None = None

    def __enter__(self) -> "ZoneTurfClient":
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

    def _get(self, url: str) -> str:
        self._patienter()
        try:
            reponse = self._client.get(url)
            reponse.raise_for_status()
        except httpx.HTTPError as exc:
            raise ImportationError(f"Échec de la requête vers Zone-Turf ({url}) : {exc}") from exc
        return reponse.text

    def recuperer_page_quinte_du_jour(self) -> str:
        return self._get(f"{BASE_URL}/quinte/")
