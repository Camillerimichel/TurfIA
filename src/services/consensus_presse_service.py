"""Service de consensus presse (niveau 3) — combine Canalturf et Zone-Turf, cf.
src/collecte/canalturf/ et src/collecte/zoneturf/.

Le consensus multi-journaux de chaque source n'existe que pour la course Quinté+
du jour (vérifié réellement pour les deux sites, cf. plan de collecte) : ce
service confirme, avant de retourner un classement, que la course demandée est
bien celle-là — indépendamment pour chaque source, puisque leurs pages/délais
sont indépendants.

Le Quinté+ du jour (page + classement) est calculé au plus une fois par
instance de service, jamais par course consultée : sans ce cache, traiter tout
un jour de courses (cf. AutomatisationService.analyser_courses_du_jour)
refaisait les 2 mêmes requêtes réseau vers Canalturf/Zone-Turf pour chaque
course — jusqu'à plusieurs minutes pour un jour complet (trouvé réellement en
test manuel le 2026-07-10 : ~10 s/course, soit >9 min pour 55 courses).
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

# Sentinel distinct de `None` (qui signifie légitimement « pas de Quinté+
# aujourd'hui ») pour repérer un cache pas encore calculé.
_NON_CALCULE = object()

QuinteResolu = tuple[int, int, list[int]]


class ConsensusPresseService:
    def __init__(self, canalturf_client: CanalturfClient, zoneturf_client: ZoneTurfClient) -> None:
        self._canalturf = canalturf_client
        self._zoneturf = zoneturf_client
        self._quinte_canalturf: QuinteResolu | None = _NON_CALCULE  # type: ignore[assignment]
        self._quinte_zoneturf: QuinteResolu | None = _NON_CALCULE  # type: ignore[assignment]

    def recuperer_classements_presse(self, numero_reunion: int, numero_course: int) -> list[list[int]]:
        """Retourne les classements consensus presse obtenus pour
        `R{numero_reunion}C{numero_course}` (0, 1 ou 2 éléments selon les sources
        qui répondent et confirment qu'il s'agit bien du Quinté+ du jour).
        L'échec d'une source (réseau, structure de page inattendue) est
        journalisé et n'empêche jamais l'autre de contribuer."""
        classements: list[list[int]] = []

        quinte_canalturf = self._recuperer_sans_lever("Canalturf", self._obtenir_quinte_canalturf)
        if quinte_canalturf is not None:
            r, c, classement = quinte_canalturf
            if (r, c) == (numero_reunion, numero_course):
                classements.append(classement)
            else:
                logger.info(
                    f"[Canalturf] La course R{numero_reunion}C{numero_course} n'est pas le Quinté+ du jour "
                    f"(R{r}C{c})."
                )

        quinte_zoneturf = self._recuperer_sans_lever("Zone-Turf", self._obtenir_quinte_zoneturf)
        if quinte_zoneturf is not None:
            r, c, classement = quinte_zoneturf
            if (r, c) == (numero_reunion, numero_course):
                classements.append(classement)
            else:
                logger.info(
                    f"[Zone-Turf] La course R{numero_reunion}C{numero_course} n'est pas le Quinté+ du jour "
                    f"(R{r}C{c})."
                )

        return classements

    def _recuperer_sans_lever(self, nom_source: str, methode) -> QuinteResolu | None:
        try:
            return methode()
        except ImportationError as exc:
            logger.warning(f"Consensus presse {nom_source} indisponible : {exc}")
            return None

    def _obtenir_quinte_canalturf(self) -> QuinteResolu | None:
        if self._quinte_canalturf is _NON_CALCULE:
            self._quinte_canalturf = self._calculer_quinte_canalturf()
        return self._quinte_canalturf

    def _calculer_quinte_canalturf(self) -> QuinteResolu | None:
        html_quinte = self._canalturf.recuperer_page_quinte_du_jour()
        url_course = extraire_url_quinte_du_jour(html_quinte)
        if url_course is None:
            logger.info("Aucun Quinté+ programmé aujourd'hui sur Canalturf.")
            return None

        html_course = self._canalturf.recuperer_page_course(url_course)
        numero_reunion_quinte, numero_course_quinte = extraire_numero_reunion_course_canalturf(html_course)
        classement = extraire_consensus_presse(html_course)
        if classement is None:
            return None
        return (numero_reunion_quinte, numero_course_quinte, classement)

    def _obtenir_quinte_zoneturf(self) -> QuinteResolu | None:
        if self._quinte_zoneturf is _NON_CALCULE:
            self._quinte_zoneturf = self._calculer_quinte_zoneturf()
        return self._quinte_zoneturf

    def _calculer_quinte_zoneturf(self) -> QuinteResolu | None:
        html_quinte = self._zoneturf.recuperer_page_quinte_du_jour()
        numeros = extraire_numero_reunion_course_zoneturf(html_quinte)
        if numeros is None:
            logger.info("Aucun Quinté+ programmé aujourd'hui sur Zone-Turf.")
            return None

        classement = extraire_synthese_presse(html_quinte)
        if classement is None:
            return None
        return (numeros[0], numeros[1], classement)
