"""Service de consensus presse (niveau 3) — cf. src/collecte/canalturf/.

Le consensus multi-journaux Canalturf n'existe que pour la course Quinté+ du jour
(cf. plan de collecte, vérifié réellement) : ce service confirme, avant de
retourner un classement, que la course demandée est bien celle-là.
"""

from __future__ import annotations

from src.collecte.canalturf.client import CanalturfClient
from src.collecte.canalturf.mappers import (
    extraire_consensus_presse,
    extraire_numero_reunion_course,
    extraire_url_quinte_du_jour,
)
from src.core.logging import get_logger

logger = get_logger("consensus_presse")


class ConsensusPresseService:
    def __init__(self, client: CanalturfClient) -> None:
        self._client = client

    def recuperer_classement_presse(self, numero_reunion: int, numero_course: int) -> list[int] | None:
        """Retourne le classement consensus presse pour `R{numero_reunion}C{numero_course}`,
        ou `None` si cette course n'est pas le Quinté+ du jour (ou si aucun Quinté+
        n'est programmé aujourd'hui)."""
        html_quinte = self._client.recuperer_page_quinte_du_jour()
        url_course = extraire_url_quinte_du_jour(html_quinte)
        if url_course is None:
            logger.info("Aucun Quinté+ programmé aujourd'hui sur Canalturf.")
            return None

        html_course = self._client.recuperer_page_course(url_course)
        numero_reunion_quinte, numero_course_quinte = extraire_numero_reunion_course(html_course)
        if (numero_reunion_quinte, numero_course_quinte) != (numero_reunion, numero_course):
            logger.info(
                f"La course R{numero_reunion}C{numero_course} n'est pas le Quinté+ du jour "
                f"(R{numero_reunion_quinte}C{numero_course_quinte})."
            )
            return None

        return extraire_consensus_presse(html_course)
