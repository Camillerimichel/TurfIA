"""Service d'orchestration de la collecte du programme du jour — cf. L015 §7,
L023 §5.2 (traitements de masse : l'échec d'une course n'interrompt pas les
suivantes).

N'utilise que l'adaptateur PMU pour l'instant (niveaux 1 et 2, cf.
src/collecte/registre.py). Conçu pour qu'un futur service de consensus presse
(niveau 3) vienne compléter les sous-scores « presse » sans changer cette méthode.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from src.collecte.pmu.client import PMUClient
from src.collecte.pmu.mappers import (
    extraire_classement,
    extraire_cote_directe,
    extraire_etat_piste_libelle,
    horodatage_depuis_epoch_ms,
    mapper_discipline_code,
    mapper_surface_code,
)
from src.core.exceptions import BusinessRuleError, ImportationError
from src.core.logging import get_logger
from src.models.course import Cheval, Cote, Course, Entraineur, Jockey, Partant, Resultat, Reunion
from src.repositories.course_repository import CourseRepository
from src.repositories.referentiel_repository import ReferentielRepository

logger = get_logger("collecte")

UNITES_DISTANCE_PMU: dict[str, str] = {"METRE": "m"}


@dataclass
class RapportCollecte:
    nb_reunions: int = 0
    nb_courses: int = 0
    nb_partants: int = 0
    erreurs: list[str] = field(default_factory=list)


class CollecteService:
    def __init__(
        self,
        pmu_client: PMUClient,
        referentiel_repository: ReferentielRepository,
        course_repository: CourseRepository,
    ) -> None:
        self._pmu = pmu_client
        self._referentiels = referentiel_repository
        self._courses = course_repository

    def collecter_programme_du_jour(self, jour: date) -> RapportCollecte:
        rapport = RapportCollecte()
        programme = self._pmu.recuperer_programme(jour)

        for reunion_brute in programme.get("programme", {}).get("reunions", []):
            try:
                reunion = self._importer_reunion(jour, reunion_brute)
            except Exception as exc:  # noqa: BLE001 - isolation volontaire par réunion
                rapport.erreurs.append(f"Réunion R{reunion_brute.get('numOfficiel')} : {exc}")
                logger.error("Échec import réunion", exc_info=exc)
                continue

            rapport.nb_reunions += 1

            # Le programme PMU signale le Quinté+ du jour au niveau réunion
            # (parisEvenement, codePari QUINTE_PLUS/E_QUINTE_PLUS) plutôt que sur
            # la course elle-même — recherché une fois par réunion.
            numeros_courses_quinte = {
                pe["course"]["numOrdre"]
                for pe in reunion_brute.get("parisEvenement", [])
                if "QUINTE_PLUS" in pe.get("codePari", "")
            }

            for course_brute in reunion_brute.get("courses", []):
                try:
                    nb_partants = self._importer_course_et_partants(
                        jour, reunion, course_brute, quinte=course_brute["numOrdre"] in numeros_courses_quinte
                    )
                except Exception as exc:  # noqa: BLE001 - isolation volontaire par course
                    ref = f"R{reunion_brute.get('numOfficiel')}C{course_brute.get('numOrdre')}"
                    rapport.erreurs.append(f"Course {ref} : {exc}")
                    logger.error("Échec import course", exc_info=exc, extra={"context": {"course": ref}})
                    continue

                rapport.nb_courses += 1
                rapport.nb_partants += nb_partants

        return rapport

    def collecter_resultats_course(self, course_id: int) -> int:
        """Récupère les cotes/résultats d'une course spécifique après son
        départ (cf. L018 §6-7, bouton « Récupérer les résultats » de la fiche
        course), sans attendre le prochain passage de la collecte horaire du
        jour ni ré-importer tout le programme. Réutilise `_importer_partant`
        (get_or_create, jamais de doublon) — mêmes données PMU
        (`recuperer_participants`) que `_importer_course_et_partants`, la
        course/réunion étant déjà connues. Retourne le nombre de partants
        traités.
        """
        course = self._courses.get_course(course_id)
        if course is None:
            raise BusinessRuleError(f"Course {course_id} introuvable.")
        reunion = self._courses.get_reunion(course.reunion_id)
        if reunion is None:
            raise BusinessRuleError(f"Réunion {course.reunion_id} introuvable pour la course {course_id}.")

        participants_bruts = self._pmu.recuperer_participants(reunion.date, reunion.numero, course.numero)
        nb_partants = 0
        for participant_brut in participants_bruts.get("participants", []):
            self._importer_partant(course, participant_brut)
            nb_partants += 1
        return nb_partants

    def _importer_reunion(self, jour: date, reunion_brute: dict) -> Reunion:
        hippodrome_brut = reunion_brute["hippodrome"]
        hippodrome = self._referentiels.get_or_create_hippodrome(
            nom=hippodrome_brut["libelleLong"],
            pays=reunion_brute.get("pays", {}).get("libelle"),
        )
        return self._courses.get_or_create_reunion(
            Reunion(date=jour, hippodrome_id=hippodrome.id, numero=reunion_brute["numOfficiel"])
        )

    def _importer_course_et_partants(
        self, jour: date, reunion: Reunion, course_brute: dict, quinte: bool = False
    ) -> int:
        discipline = self._referentiels.get_or_create_discipline(mapper_discipline_code(course_brute["discipline"]))

        unite = UNITES_DISTANCE_PMU.get(course_brute.get("distanceUnit", ""))
        if unite is None:
            raise ImportationError(f"Unité de distance PMU inconnue : '{course_brute.get('distanceUnit')}'.")
        distance = self._referentiels.get_or_create_distance(course_brute["distance"], unite)

        surface_libelle = mapper_surface_code(course_brute.get("typePiste"))
        surface = self._referentiels.get_or_create_surface(surface_libelle) if surface_libelle else None

        etat_piste_libelle = extraire_etat_piste_libelle(course_brute)
        etat_piste = self._referentiels.get_or_create_etat_piste(etat_piste_libelle) if etat_piste_libelle else None

        course = self._courses.get_or_create_course(
            Course(
                reunion_id=reunion.id,
                numero=course_brute["numOrdre"],
                nom=course_brute["libelle"],
                heure_depart=horodatage_depuis_epoch_ms(course_brute.get("heureDepart")),
                discipline_id=discipline.id,
                distance_id=distance.id,
                surface_id=surface.id if surface else None,
                etat_piste_id=etat_piste.id if etat_piste else None,
                allocation=course_brute.get("montantPrix"),
                nb_partants=course_brute.get("nombreDeclaresPartants"),
                quinte=quinte,
            )
        )

        participants_bruts = self._pmu.recuperer_participants(jour, reunion.numero, course.numero)
        nb_partants = 0
        for participant_brut in participants_bruts.get("participants", []):
            self._importer_partant(course, participant_brut)
            nb_partants += 1
        return nb_partants

    def _importer_partant(self, course: Course, participant_brut: dict) -> None:
        cheval = self._courses.get_or_create_cheval(Cheval(nom=participant_brut["nom"]))

        jockey_id = None
        if participant_brut.get("driver"):
            jockey_id = self._courses.get_or_create_jockey(Jockey(nom=participant_brut["driver"])).id

        entraineur_id = None
        if participant_brut.get("entraineur"):
            entraineur_id = self._courses.get_or_create_entraineur(Entraineur(nom=participant_brut["entraineur"])).id

        partant = self._courses.get_or_create_partant(
            Partant(
                course_id=course.id,
                cheval_id=cheval.id,
                numero=participant_brut["numPmu"],
                jockey_id=jockey_id,
                entraineur_id=entraineur_id,
                age=participant_brut.get("age"),
                non_partant=participant_brut.get("statut") == "NON_PARTANT",
            )
        )

        cote = extraire_cote_directe(participant_brut)
        if cote is not None:
            self._courses.create_cote(Cote(partant_id=partant.id, operateur="PMU", cote=cote))

        classement = extraire_classement(participant_brut)
        if classement is not None:
            self._courses.get_or_create_resultat(
                Resultat(course_id=course.id, partant_id=partant.id, classement=classement)
            )
