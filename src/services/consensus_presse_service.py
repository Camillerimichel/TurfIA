"""Service de consensus presse (niveau 3) — combine Canalturf et Zone-Turf, cf.
src/collecte/canalturf/ et src/collecte/zoneturf/.

Le consensus multi-journaux de chaque source n'existe que pour la course Quinté+
du jour (vérifié réellement pour les deux sites, cf. plan de collecte) : ce
service confirme, avant de retourner un classement, que la course demandée est
bien celle-là — indépendamment pour chaque source, puisque leurs pages/délais
sont indépendants.
"""

from __future__ import annotations

from src.collecte.canalturf.client import CanalturfClient
from src.collecte.canalturf.mappers import (
    extraire_consensus_presse,
    extraire_numero_reunion_course as extraire_numero_reunion_course_canalturf,
    extraire_url_quinte_du_jour,
)
from src.collecte.zoneturf.client import ZoneTurfClient
from src.collecte.zoneturf.mappers import (
    extraire_numero_reunion_course as extraire_numero_reunion_course_zoneturf,
    extraire_synthese_presse,
)
from src.core.exceptions import ImportationError
from src.core.logging import get_logger

logger = get_logger("consensus_presse")


class ConsensusPresseService:
    def __init__(self, canalturf_client: CanalturfClient, zoneturf_client: ZoneTurfClient) -> None:
        self._canalturf = canalturf_client
        self._zoneturf = zoneturf_client

    def recuperer_classements_presse(self, numero_reunion: int, numero_course: int) -> list[list[int]]:
        """Retourne les classements consensus presse obtenus pour
        `R{numero_reunion}C{numero_course}` (0, 1 ou 2 éléments selon les sources
        qui répondent et confirment qu'il s'agit bien du Quinté+ du jour).
        L'échec d'une source (réseau, structure de page inattendue) est
        journalisé et n'empêche jamais l'autre de contribuer."""
        classements: list[list[int]] = []

        classement_canalturf = self._recuperer_sans_lever(
            "Canalturf", self._recuperer_canalturf, numero_reunion, numero_course
        )
        if classement_canalturf is not None:
            classements.append(classement_canalturf)

        classement_zoneturf = self._recuperer_sans_lever(
            "Zone-Turf", self._recuperer_zoneturf, numero_reunion, numero_course
        )
        if classement_zoneturf is not None:
            classements.append(classement_zoneturf)

        return classements

    def _recuperer_sans_lever(
        self, nom_source: str, methode, numero_reunion: int, numero_course: int
    ) -> list[int] | None:
        try:
            return methode(numero_reunion, numero_course)
        except ImportationError as exc:
            logger.warning(
                f"Consensus presse {nom_source} indisponible : {exc}",
                extra={"context": {"numero_reunion": numero_reunion, "numero_course": numero_course}},
            )
            return None

    def _recuperer_canalturf(self, numero_reunion: int, numero_course: int) -> list[int] | None:
        html_quinte = self._canalturf.recuperer_page_quinte_du_jour()
        url_course = extraire_url_quinte_du_jour(html_quinte)
        if url_course is None:
            logger.info("Aucun Quinté+ programmé aujourd'hui sur Canalturf.")
            return None

        html_course = self._canalturf.recuperer_page_course(url_course)
        numero_reunion_quinte, numero_course_quinte = extraire_numero_reunion_course_canalturf(html_course)
        if (numero_reunion_quinte, numero_course_quinte) != (numero_reunion, numero_course):
            logger.info(
                f"[Canalturf] La course R{numero_reunion}C{numero_course} n'est pas le Quinté+ du jour "
                f"(R{numero_reunion_quinte}C{numero_course_quinte})."
            )
            return None

        return extraire_consensus_presse(html_course)

    def _recuperer_zoneturf(self, numero_reunion: int, numero_course: int) -> list[int] | None:
        html_quinte = self._zoneturf.recuperer_page_quinte_du_jour()
        numeros = extraire_numero_reunion_course_zoneturf(html_quinte)
        if numeros is None:
            logger.info("Aucun Quinté+ programmé aujourd'hui sur Zone-Turf.")
            return None

        if numeros != (numero_reunion, numero_course):
            logger.info(
                f"[Zone-Turf] La course R{numero_reunion}C{numero_course} n'est pas le Quinté+ du jour "
                f"(R{numeros[0]}C{numeros[1]})."
            )
            return None

        return extraire_synthese_presse(html_quinte)
