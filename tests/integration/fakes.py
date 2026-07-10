"""Repositories en mémoire pour les tests d'intégration API (sans base réelle).

Implémentent la même interface que les repositories SQL (cf. src/repositories/),
ce qui permet de tester le câblage FastAPI (routes -> schémas -> dépendances ->
gestion d'erreurs) sans dépendre d'une instance PostgreSQL (cf. L020 §5.2).
"""

from __future__ import annotations

import dataclasses
import itertools
from datetime import datetime, timezone

from src.core.exceptions import BusinessRuleError, ImportationError
from src.models.audit import Audit
from src.models.historique import HistoriqueLigne
from src.models.referentiels import Discipline, Distance, EtatPiste, Hippodrome, Surface
from src.models.technique import Journal, Tache
from src.services.collecte_service import RapportCollecte
from src.services.supervision_service import EtatSupervision


class _AutoId:
    def __init__(self) -> None:
        self._counter = itertools.count(1)

    def next(self) -> int:
        return next(self._counter)


class FakeReferentielRepository:
    def __init__(self) -> None:
        self._ids = _AutoId()
        self.hippodromes: dict[int, object] = {}
        self.disciplines: dict[int, object] = {}
        self.types_course: dict[int, object] = {}
        self.distances: dict[int, object] = {}
        self.surfaces: dict[int, object] = {}
        self.etats_piste: dict[int, object] = {}

    def seed_hippodrome(self, hippodrome) -> object:
        hippodrome = dataclasses.replace(hippodrome, id=self._ids.next())
        self.hippodromes[hippodrome.id] = hippodrome
        return hippodrome

    def get_hippodrome(self, hippodrome_id: int):
        return self.hippodromes.get(hippodrome_id)

    def list_hippodromes(self):
        return list(self.hippodromes.values())

    def seed_discipline(self, discipline) -> object:
        discipline = dataclasses.replace(discipline, id=self._ids.next())
        self.disciplines[discipline.id] = discipline
        return discipline

    def get_discipline(self, discipline_id: int):
        return self.disciplines.get(discipline_id)

    def seed_type_course(self, type_course) -> object:
        type_course = dataclasses.replace(type_course, id=self._ids.next())
        self.types_course[type_course.id] = type_course
        return type_course

    def get_type_course(self, type_course_id: int):
        return self.types_course.get(type_course_id)

    def seed_distance(self, distance) -> object:
        distance = dataclasses.replace(distance, id=self._ids.next())
        self.distances[distance.id] = distance
        return distance

    def get_distance(self, distance_id: int):
        return self.distances.get(distance_id)

    def seed_surface(self, surface) -> object:
        surface = dataclasses.replace(surface, id=self._ids.next())
        self.surfaces[surface.id] = surface
        return surface

    def get_surface(self, surface_id: int):
        return self.surfaces.get(surface_id)

    def seed_etat_piste(self, etat_piste) -> object:
        etat_piste = dataclasses.replace(etat_piste, id=self._ids.next())
        self.etats_piste[etat_piste.id] = etat_piste
        return etat_piste

    def get_etat_piste(self, etat_piste_id: int):
        return self.etats_piste.get(etat_piste_id)

    # -- get-or-create : utilisées par CollecteService (cf. src/repositories/
    # referentiel_repository.py, même sémantique idempotente par nom/libellé) --

    def get_or_create_hippodrome(self, nom: str, ville: str | None = None, pays: str | None = None):
        existant = next((h for h in self.hippodromes.values() if h.nom == nom), None)
        return existant if existant is not None else self.seed_hippodrome(Hippodrome(nom=nom, ville=ville, pays=pays))

    def get_or_create_discipline(self, libelle: str):
        existant = next((d for d in self.disciplines.values() if d.libelle == libelle), None)
        return existant if existant is not None else self.seed_discipline(Discipline(libelle=libelle))

    def get_or_create_surface(self, libelle: str):
        existant = next((s for s in self.surfaces.values() if s.libelle == libelle), None)
        return existant if existant is not None else self.seed_surface(Surface(libelle=libelle))

    def get_or_create_etat_piste(self, libelle: str):
        existant = next((e for e in self.etats_piste.values() if e.libelle == libelle), None)
        return existant if existant is not None else self.seed_etat_piste(EtatPiste(libelle=libelle))

    def get_or_create_distance(self, distance: int, unite: str = "m"):
        existant = next((d for d in self.distances.values() if d.distance == distance and d.unite == unite), None)
        return existant if existant is not None else self.seed_distance(Distance(distance=distance, unite=unite))


class FakeCourseRepository:
    def __init__(self, referentiel_repo: "FakeReferentielRepository | None" = None) -> None:
        self._ids = _AutoId()
        self._referentiels = referentiel_repo
        self.reunions: dict[int, object] = {}
        self.courses: dict[int, object] = {}
        self.chevaux: dict[int, object] = {}
        self.jockeys: dict[int, object] = {}
        self.entraineurs: dict[int, object] = {}
        self.partants: dict[int, object] = {}
        self.cotes: dict[int, float] = {}  # dernière cote par partant_id (simplifié pour les tests)
        self.cotes_historique: dict[int, list] = {}  # toutes les cotes par partant_id, dans l'ordre d'insertion
        self.resultats: dict[int, object] = {}
        # (victoires, courses) configurables par les tests ; absent = (0, 0) (échantillon nul -> score neutre).
        self.performances_jockey: dict[int, tuple[int, int]] = {}
        self.performances_entraineur: dict[int, tuple[int, int]] = {}
        self.performances_couple: dict[tuple[int, int], tuple[int, int]] = {}
        self.performances_conditions: dict[tuple[int, int, int, int], tuple[int, int]] = {}

    @staticmethod
    def _appliquer_patch(store: dict, resource_id: int, champs: dict):
        actuel = store.get(resource_id)
        if actuel is None:
            return None
        mis_a_jour = dataclasses.replace(actuel, **champs) if champs else actuel
        store[resource_id] = mis_a_jour
        return mis_a_jour

    @staticmethod
    def _supprimer(store: dict, ressource_id: int, nom_ressource: str, references: bool) -> bool:
        """Simule la contrainte FK ON DELETE RESTRICT réelle (cf.
        CourseRepository._supprimer) : `references` est calculé par l'appelant à
        partir des autres stores en mémoire."""
        if ressource_id not in store:
            return False
        if references:
            raise BusinessRuleError(
                f"Impossible de supprimer {nom_ressource} {ressource_id} : des données y sont rattachées."
            )
        del store[ressource_id]
        return True

    def create_reunion(self, reunion):
        reunion = dataclasses.replace(reunion, id=self._ids.next())
        self.reunions[reunion.id] = reunion
        return reunion

    def _avec_hippodrome_nom(self, reunion):
        if reunion is None or self._referentiels is None:
            return reunion
        hippodrome = self._referentiels.hippodromes.get(reunion.hippodrome_id)
        if hippodrome is None:
            return reunion
        return dataclasses.replace(reunion, hippodrome_nom=hippodrome.nom)

    def get_reunion(self, reunion_id: int):
        return self._avec_hippodrome_nom(self.reunions.get(reunion_id))

    def list_reunions_by_date(self, jour, hippodrome_id: int | None = None):
        reunions = (
            r
            for r in self.reunions.values()
            if r.date == jour and (hippodrome_id is None or r.hippodrome_id == hippodrome_id)
        )
        return [self._avec_hippodrome_nom(r) for r in sorted(reunions, key=lambda r: r.numero)]

    def update_reunion(self, reunion_id: int, champs: dict):
        return self._appliquer_patch(self.reunions, reunion_id, champs)

    def delete_reunion(self, reunion_id: int) -> bool:
        references = any(c.reunion_id == reunion_id for c in self.courses.values())
        return self._supprimer(self.reunions, reunion_id, "la réunion", references)

    def get_or_create_reunion(self, reunion):
        existant = next(
            (
                r
                for r in self.reunions.values()
                if r.date == reunion.date and r.hippodrome_id == reunion.hippodrome_id and r.numero == reunion.numero
            ),
            None,
        )
        return existant if existant is not None else self.create_reunion(reunion)

    def create_course(self, course):
        course = dataclasses.replace(course, id=self._ids.next())
        self.courses[course.id] = course
        return course

    def get_course(self, course_id: int):
        return self.courses.get(course_id)

    def update_course(self, course_id: int, champs: dict):
        return self._appliquer_patch(self.courses, course_id, champs)

    def delete_course(self, course_id: int) -> bool:
        references = any(p.course_id == course_id for p in self.partants.values()) or any(
            r.course_id == course_id for r in self.resultats.values()
        )
        return self._supprimer(self.courses, course_id, "la course", references)

    def get_or_create_course(self, course):
        existant = next(
            (c for c in self.courses.values() if c.reunion_id == course.reunion_id and c.numero == course.numero),
            None,
        )
        return existant if existant is not None else self.create_course(course)

    def list_courses_by_reunion(self, reunion_id: int):
        return [c for c in self.courses.values() if c.reunion_id == reunion_id]

    def list_courses_avec_resultat(self, date_debut, date_fin):
        courses_avec_resultat = {r.course_id for r in self.resultats.values()}
        courses = [
            c
            for c in self.courses.values()
            if c.id in courses_avec_resultat and date_debut <= self.reunions[c.reunion_id].date <= date_fin
        ]
        return sorted(courses, key=lambda c: (self.reunions[c.reunion_id].date, c.numero))

    def create_cheval(self, cheval):
        cheval = dataclasses.replace(cheval, id=self._ids.next())
        self.chevaux[cheval.id] = cheval
        return cheval

    def get_cheval(self, cheval_id: int):
        return self.chevaux.get(cheval_id)

    def update_cheval(self, cheval_id: int, champs: dict):
        return self._appliquer_patch(self.chevaux, cheval_id, champs)

    def delete_cheval(self, cheval_id: int) -> bool:
        references = any(p.cheval_id == cheval_id for p in self.partants.values())
        return self._supprimer(self.chevaux, cheval_id, "le cheval", references)

    def get_or_create_cheval(self, cheval):
        existant = next((c for c in self.chevaux.values() if c.nom == cheval.nom), None)
        return existant if existant is not None else self.create_cheval(cheval)

    def create_jockey(self, jockey):
        jockey = dataclasses.replace(jockey, id=self._ids.next())
        self.jockeys[jockey.id] = jockey
        return jockey

    def get_jockey(self, jockey_id: int):
        return self.jockeys.get(jockey_id)

    def update_jockey(self, jockey_id: int, champs: dict):
        return self._appliquer_patch(self.jockeys, jockey_id, champs)

    def delete_jockey(self, jockey_id: int) -> bool:
        references = any(p.jockey_id == jockey_id for p in self.partants.values())
        return self._supprimer(self.jockeys, jockey_id, "le jockey", references)

    def get_or_create_jockey(self, jockey):
        existant = next((j for j in self.jockeys.values() if j.nom == jockey.nom), None)
        return existant if existant is not None else self.create_jockey(jockey)

    def create_entraineur(self, entraineur):
        entraineur = dataclasses.replace(entraineur, id=self._ids.next())
        self.entraineurs[entraineur.id] = entraineur
        return entraineur

    def get_entraineur(self, entraineur_id: int):
        return self.entraineurs.get(entraineur_id)

    def update_entraineur(self, entraineur_id: int, champs: dict):
        return self._appliquer_patch(self.entraineurs, entraineur_id, champs)

    def delete_entraineur(self, entraineur_id: int) -> bool:
        references = any(p.entraineur_id == entraineur_id for p in self.partants.values())
        return self._supprimer(self.entraineurs, entraineur_id, "l'entraîneur", references)

    def get_or_create_entraineur(self, entraineur):
        existant = next((e for e in self.entraineurs.values() if e.nom == entraineur.nom), None)
        return existant if existant is not None else self.create_entraineur(entraineur)

    def create_partant(self, partant):
        partant = dataclasses.replace(partant, id=self._ids.next())
        self.partants[partant.id] = partant
        return partant

    def get_partant(self, partant_id: int):
        return self.partants.get(partant_id)

    def update_partant(self, partant_id: int, champs: dict):
        return self._appliquer_patch(self.partants, partant_id, champs)

    def delete_partant(self, partant_id: int) -> bool:
        references = any(r.partant_id == partant_id for r in self.resultats.values()) or (
            partant_id in self.cotes_historique and len(self.cotes_historique[partant_id]) > 0
        )
        return self._supprimer(self.partants, partant_id, "le partant", references)

    def get_or_create_partant(self, partant):
        existant = next(
            (p for p in self.partants.values() if p.course_id == partant.course_id and p.numero == partant.numero),
            None,
        )
        return existant if existant is not None else self.create_partant(partant)

    def list_partants_by_course(self, course_id: int):
        return [p for p in self.partants.values() if p.course_id == course_id]

    def list_partants_detail_by_course(self, course_id: int):
        from src.models.course import PartantDetail

        resultats = []
        for p in sorted(self.list_partants_by_course(course_id), key=lambda p: p.numero):
            cheval = self.chevaux.get(p.cheval_id)
            jockey = self.jockeys.get(p.jockey_id) if p.jockey_id is not None else None
            entraineur = self.entraineurs.get(p.entraineur_id) if p.entraineur_id is not None else None
            cotes = self.cotes_historique.get(p.id, [])
            derniere = max(cotes, key=lambda c: c.date_maj) if cotes else None
            resultats.append(
                PartantDetail(
                    id=p.id, course_id=p.course_id, cheval_id=p.cheval_id, numero=p.numero,
                    cheval_nom=cheval.nom if cheval else f"#{p.cheval_id}",
                    jockey_id=p.jockey_id, jockey_nom=jockey.nom if jockey else None,
                    jockey_prenom=jockey.prenom if jockey else None,
                    entraineur_id=p.entraineur_id, entraineur_nom=entraineur.nom if entraineur else None,
                    entraineur_prenom=entraineur.prenom if entraineur else None,
                    corde=p.corde, poids=p.poids, valeur=p.valeur, age=p.age, ferrure=p.ferrure,
                    musique=p.musique, non_partant=p.non_partant,
                    derniere_cote=derniere.cote if derniere else None,
                    derniere_cote_operateur=derniere.operateur if derniere else None,
                )
            )
        return resultats

    def create_cote(self, cote):
        cote = dataclasses.replace(
            cote, id=self._ids.next(), date_maj=cote.date_maj or datetime.now(timezone.utc)
        )
        self.cotes[cote.partant_id] = cote.cote
        self.cotes_historique.setdefault(cote.partant_id, []).append(cote)
        return cote

    def list_cotes_by_partant(self, partant_id: int):
        return list(reversed(self.cotes_historique.get(partant_id, [])))

    def get_or_create_resultat(self, resultat):
        existant = next(
            (
                r
                for r in self.resultats.values()
                if r.course_id == resultat.course_id and r.classement == resultat.classement
            ),
            None,
        )
        if existant is not None:
            return existant
        resultat = dataclasses.replace(resultat, id=self._ids.next())
        self.resultats[resultat.id] = resultat
        return resultat

    def list_resultats_by_course(self, course_id: int):
        return [r for r in self.resultats.values() if r.course_id == course_id]

    def get_dernieres_cotes_par_course(self, course_id: int) -> dict[int, float]:
        return {p.id: self.cotes[p.id] for p in self.list_partants_by_course(course_id) if p.id in self.cotes}

    def compter_performances_jockey(self, jockey_id: int, exclure_course_id: int) -> tuple[int, int]:
        return self.performances_jockey.get(jockey_id, (0, 0))

    def compter_performances_entraineur(self, entraineur_id: int, exclure_course_id: int) -> tuple[int, int]:
        return self.performances_entraineur.get(entraineur_id, (0, 0))

    def compter_performances_couple(self, jockey_id: int, entraineur_id: int, exclure_course_id: int) -> tuple[int, int]:
        return self.performances_couple.get((jockey_id, entraineur_id), (0, 0))

    def compter_performances_cheval_conditions(
        self, cheval_id: int, distance_id: int, surface_id: int, etat_piste_id: int, exclure_course_id: int
    ) -> tuple[int, int]:
        return self.performances_conditions.get((cheval_id, distance_id, surface_id, etat_piste_id), (0, 0))


class FakeAnalyseRepository:
    def __init__(self) -> None:
        self._ids = _AutoId()
        self.analyses: dict[int, object] = {}
        self.analyse_partants: dict[int, list] = {}
        self.selections: dict[int, list] = {}
        self.paris: dict[int, list] = {}
        self.controle_rois: dict[int, object] = {}  # keyed by analyse_id
        self.controle_roi_paris: dict[int, object] = {}  # keyed by pari_id

    def create_analyse(self, analyse):
        # Reproduit la contrainte UNIQUE(course_id, version) réelle (cf.
        # sql/schema/03_analyses.sql, AnalyseRepository.create_analyse) : sans
        # ce contrôle, le fake acceptait silencieusement des doublons que
        # PostgreSQL rejette en vrai, cachant en test un vrai 409 de l'API.
        if any(a.course_id == analyse.course_id and a.version == analyse.version for a in self.analyses.values()):
            raise BusinessRuleError(
                f"Une analyse existe déjà pour la course {analyse.course_id} en version {analyse.version}."
            )
        # `date_calcul` par défaut à `now()` côté SQL réel (cf. sql/schema/03_analyses.sql) —
        # reproduit ici puisque `AnalyseService.analyser_course` ne la fixe jamais lui-même.
        date_calcul = analyse.date_calcul if analyse.date_calcul is not None else datetime.now(timezone.utc)
        analyse = dataclasses.replace(analyse, id=self._ids.next(), date_calcul=date_calcul)
        self.analyses[analyse.id] = analyse
        self.analyse_partants[analyse.id] = []
        self.selections[analyse.id] = []
        self.paris[analyse.id] = []
        return analyse

    def get_analyse(self, analyse_id: int):
        return self.analyses.get(analyse_id)

    def list_analyses_by_course(self, course_id: int):
        return [a for a in self.analyses.values() if a.course_id == course_id]

    def get_derniere_version(self, course_id: int) -> int:
        versions = [a.version for a in self.analyses.values() if a.course_id == course_id]
        return max(versions) if versions else 0

    def create_analyse_partant(self, ap):
        ap = dataclasses.replace(ap, id=self._ids.next())
        self.analyse_partants[ap.analyse_id].append(ap)
        return ap

    def list_analyse_partants(self, analyse_id: int):
        return list(self.analyse_partants.get(analyse_id, []))

    def create_selection(self, selection):
        selection = dataclasses.replace(selection, id=self._ids.next())
        self.selections[selection.analyse_id].append(selection)
        return selection

    def list_selections_by_analyse(self, analyse_id: int):
        return list(self.selections.get(analyse_id, []))

    def create_pari(self, pari):
        pari = dataclasses.replace(pari, id=self._ids.next())
        self.paris[pari.analyse_id].append(pari)
        return pari

    def list_paris_by_analyse(self, analyse_id: int):
        return list(self.paris.get(analyse_id, []))

    def list_analyses_sans_controle_roi(self):
        return [
            a
            for a in self.analyses.values()
            if a.id not in self.controle_rois and self.paris.get(a.id)
        ]

    def create_controle_roi(self, controle):
        controle = dataclasses.replace(controle, id=self._ids.next())
        self.controle_rois[controle.analyse_id] = controle
        return controle

    def create_controle_roi_pari(self, controle):
        controle = dataclasses.replace(controle, id=self._ids.next())
        self.controle_roi_paris[controle.pari_id] = controle
        return controle


class FakePMUClient:
    """Remplace PMUClient dans les tests d'intégration — aucun accès réseau (cf.
    L020 §2.2). `rapports_par_course` associe (numero_reunion, numero_course) à la
    réponse brute simulée de /rapports-definitifs ; `programme` est la réponse
    brute simulée de /programme (ou `None` -> erreur) ; `participants_par_course`
    associe (numero_reunion, numero_course) à la réponse brute simulée de
    /participants (cf. CollecteService)."""

    def __init__(
        self,
        rapports_par_course: dict | None = None,
        programme: dict | None = None,
        participants_par_course: dict | None = None,
    ) -> None:
        self.rapports_par_course = rapports_par_course or {}
        self.programme = programme
        self.participants_par_course = participants_par_course or {}

    def recuperer_rapports_definitifs(self, jour, num_reunion: int, num_course: int) -> list[dict]:
        cle = (num_reunion, num_course)
        if cle not in self.rapports_par_course:
            raise ImportationError(f"Rapports non disponibles pour R{num_reunion}C{num_course} (simulé).")
        return self.rapports_par_course[cle]

    def recuperer_programme(self, jour) -> dict:
        if self.programme is None:
            raise ImportationError("Programme non disponible (simulé).")
        return self.programme

    def recuperer_participants(self, jour, num_reunion: int, num_course: int) -> dict:
        cle = (num_reunion, num_course)
        if cle not in self.participants_par_course:
            raise ImportationError(f"Participants non disponibles pour R{num_reunion}C{num_course} (simulé).")
        return self.participants_par_course[cle]


class FakeUtilisateurRepository:
    def __init__(self) -> None:
        self._ids = _AutoId()
        self.roles: dict[int, object] = {}
        self.utilisateurs: dict[int, object] = {}
        self.sessions: dict[str, object] = {}  # jeton_hache -> Session

    def seed_role(self, role):
        role = dataclasses.replace(role, id=self._ids.next())
        self.roles[role.id] = role
        return role

    def seed_utilisateur(self, utilisateur):
        utilisateur = dataclasses.replace(utilisateur, id=self._ids.next())
        self.utilisateurs[utilisateur.id] = utilisateur
        return utilisateur

    def get_role_par_nom(self, nom: str):
        return next((r for r in self.roles.values() if r.nom == nom), None)

    def get_role_par_id(self, role_id: int):
        return self.roles.get(role_id)

    def get_utilisateur_par_login(self, login: str):
        return next((u for u in self.utilisateurs.values() if u.login == login), None)

    def creer_utilisateur(self, utilisateur):
        return self.seed_utilisateur(utilisateur)

    def mettre_a_jour_derniere_connexion(self, utilisateur_id: int) -> None:
        u = self.utilisateurs[utilisateur_id]
        self.utilisateurs[utilisateur_id] = dataclasses.replace(u, derniere_connexion="now")

    def creer_session(self, session):
        session = dataclasses.replace(session, id=self._ids.next())
        self.sessions[session.jeton_hache] = session
        return session

    def get_utilisateur_par_session_active(self, jeton_hache: str):
        session = self.sessions.get(jeton_hache)
        if session is None or session.revoque_le is not None:
            return None
        if session.expire_le <= datetime.now(timezone.utc):
            return None
        utilisateur = self.utilisateurs.get(session.utilisateur_id)
        if utilisateur is None or not utilisateur.actif:
            return None
        role = self.roles.get(utilisateur.role_id)
        return utilisateur, role

    def marquer_utilisation_session(self, jeton_hache: str) -> None:
        pass

    def revoquer_session(self, jeton_hache: str) -> None:
        session = self.sessions.get(jeton_hache)
        if session is not None:
            self.sessions[jeton_hache] = dataclasses.replace(session, revoque_le="revoked")


class FakeAuditRepository:
    def __init__(self) -> None:
        self._ids = _AutoId()
        self.entrees: list[Audit] = []

    def enregistrer(
        self,
        utilisateur_id,
        action: str,
        objet: str | None = None,
        ancien_etat: str | None = None,
        nouvel_etat: str | None = None,
    ) -> None:
        self.entrees.append(
            Audit(
                id=self._ids.next(),
                utilisateur_id=utilisateur_id,
                date_action=datetime.now(timezone.utc),
                action=action,
                objet=objet,
                ancien_etat=ancien_etat,
                nouvel_etat=nouvel_etat,
            )
        )

    def lister(self, limite: int = 200) -> list[Audit]:
        return list(reversed(self.entrees))[:limite]


class FakeConsensusPresseService:
    """Remplace ConsensusPresseService dans les tests d'intégration — aucun accès
    réseau (cf. L020 §2.2). `classements` (0, 1 ou 2 classements, un par source
    simulée) est configurable par le test."""

    def __init__(self, classements: list[list[int]] | None = None) -> None:
        self.classements = classements if classements is not None else []

    def recuperer_classements_presse(self, numero_reunion: int, numero_course: int) -> list[list[int]]:
        return self.classements


class FakeStatistiqueRepository:
    """Remplace StatistiqueRepository — pas de recalcul d'agrégation en mémoire
    (déjà vérifié contre une instance PostgreSQL réelle, cf. PROJECT_STATE.md) :
    `calculer_X` retourne des valeurs configurables par le test, `create_X` les
    stocke simplement (jamais de mise à jour, comme le vrai repository)."""

    def __init__(self) -> None:
        self._ids = _AutoId()
        self.a_calculer_globale = None
        self.a_calculer_scores: list = []
        self.a_calculer_hippodromes: list = []
        self.a_calculer_disciplines: list = []
        self.a_calculer_paris: list = []
        self.a_calculer_modeles: list = []
        self.globale: list = []
        self.scores: list = []
        self.hippodromes: list = []
        self.disciplines: list = []
        self.paris: list = []
        self.modeles: list = []

    def calculer_globale(self):
        return self.a_calculer_globale

    def create_globale(self, stat):
        stat = dataclasses.replace(stat, id=self._ids.next(), date_calcul=stat.date_calcul or datetime.now(timezone.utc))
        self.globale.append(stat)
        return stat

    def calculer_scores(self):
        return self.a_calculer_scores

    def create_score(self, stat):
        stat = dataclasses.replace(stat, id=self._ids.next())
        self.scores.append(stat)
        return stat

    def calculer_hippodromes(self):
        return self.a_calculer_hippodromes

    def create_hippodrome(self, stat):
        stat = dataclasses.replace(stat, id=self._ids.next())
        self.hippodromes.append(stat)
        return stat

    def get_dernier_hippodrome(self, hippodrome_id: int):
        candidats = [h for h in self.hippodromes if h.hippodrome_id == hippodrome_id]
        return candidats[-1] if candidats else None

    def calculer_disciplines(self):
        return self.a_calculer_disciplines

    def create_discipline(self, stat):
        stat = dataclasses.replace(stat, id=self._ids.next())
        self.disciplines.append(stat)
        return stat

    def calculer_paris(self):
        return self.a_calculer_paris

    def create_pari_stat(self, stat):
        stat = dataclasses.replace(stat, id=self._ids.next())
        self.paris.append(stat)
        return stat

    def calculer_modeles(self):
        return self.a_calculer_modeles

    def create_modele(self, stat):
        stat = dataclasses.replace(stat, id=self._ids.next())
        self.modeles.append(stat)
        return stat

    def list_globale(self):
        return list(self.globale)

    def list_scores(self):
        return list(self.scores)

    def list_hippodromes(self):
        return list(self.hippodromes)

    def list_disciplines(self):
        return list(self.disciplines)

    def list_paris(self):
        return list(self.paris)

    def list_modeles(self):
        return list(self.modeles)


class FakeHistoriqueRepository:
    """Recompose en mémoire la jointure SQL réelle (reunion -> course -> analyses
    -> pari -> controle_roi_pari) à partir des stores déjà exposés par
    `FakeCourseRepository`/`FakeAnalyseRepository`/`FakeReferentielRepository`."""

    def __init__(self, course_repo: FakeCourseRepository, analyse_repo: "FakeAnalyseRepository", referentiel_repo: FakeReferentielRepository) -> None:
        self._courses = course_repo
        self._analyses = analyse_repo
        self._referentiels = referentiel_repo

    def rechercher(self, filtres) -> list[HistoriqueLigne]:
        lignes: list[HistoriqueLigne] = []
        for reunion in self._courses.reunions.values():
            if filtres.date_debut is not None and reunion.date < filtres.date_debut:
                continue
            if filtres.date_fin is not None and reunion.date > filtres.date_fin:
                continue
            if filtres.hippodrome_id is not None and reunion.hippodrome_id != filtres.hippodrome_id:
                continue
            hippodrome = self._referentiels.hippodromes.get(reunion.hippodrome_id)
            hippodrome_nom = hippodrome.nom if hippodrome is not None else "?"

            for course in self._courses.list_courses_by_reunion(reunion.id):
                for analyse in self._analyses.list_analyses_by_course(course.id):
                    if filtres.decision is not None and analyse.decision != filtres.decision:
                        continue
                    base = dict(
                        date=reunion.date, hippodrome_id=reunion.hippodrome_id, hippodrome_nom=hippodrome_nom,
                        course_id=course.id, course_numero=course.numero, course_nom=course.nom,
                        analyse_id=analyse.id, version=analyse.version, date_calcul=analyse.date_calcul,
                        decision=analyse.decision,
                        score_confiance=analyse.score_confiance, risque=analyse.risque, budget=analyse.budget,
                    )
                    paris = self._analyses.list_paris_by_analyse(analyse.id)
                    if not paris:
                        if filtres.type_pari is not None:
                            continue
                        lignes.append(HistoriqueLigne(**base))
                        continue
                    for pari in paris:
                        if filtres.type_pari is not None and pari.type_pari != filtres.type_pari:
                            continue
                        controle = self._analyses.controle_roi_paris.get(pari.id)
                        lignes.append(HistoriqueLigne(
                            **base, pari_id=pari.id, type_pari=pari.type_pari, mise=pari.mise,
                            gain_estime=pari.gain_estime, roi_estime=pari.roi_estime,
                            roi_reel=controle.roi if controle else None,
                            profit_reel=controle.profit if controle else None,
                            valide=controle.valide if controle else None,
                        ))
        lignes.sort(key=lambda l: (l.date, l.course_numero, l.version), reverse=True)
        return lignes[: filtres.limite]


class FakeJournalRepository:
    def __init__(self) -> None:
        self._ids = _AutoId()
        self.journaux: list[Journal] = []

    def enregistrer(self, niveau: str, message: str, composant=None, correlation_id=None, exception=None) -> Journal:
        journal = Journal(
            id=self._ids.next(), niveau=niveau, message=message, composant=composant,
            correlation_id=correlation_id, exception=exception, date_evenement=datetime.now(timezone.utc),
        )
        self.journaux.append(journal)
        return journal

    def lister(self, niveau=None, composant=None, date_debut=None, date_fin=None, limite: int = 200) -> list[Journal]:
        resultat = [
            j for j in self.journaux
            if (niveau is None or j.niveau == niveau)
            and (composant is None or j.composant == composant)
            and (date_debut is None or j.date_evenement.date() >= date_debut)
            and (date_fin is None or j.date_evenement.date() <= date_fin)
        ]
        return list(reversed(resultat))[:limite]


class FakeTacheRepository:
    def __init__(self) -> None:
        self._ids = _AutoId()
        self.taches: dict[int, Tache] = {}

    def demarrer(self, nom: str, categorie: str | None = None) -> Tache:
        tache = Tache(id=self._ids.next(), nom=nom, categorie=categorie, debut=datetime.now(timezone.utc), statut="en_cours")
        self.taches[tache.id] = tache
        return tache

    def terminer(self, tache_id: int, statut: str, commentaire: str | None = None) -> Tache | None:
        tache = self.taches.get(tache_id)
        if tache is None:
            return None
        fin = datetime.now(timezone.utc)
        duree_ms = int((fin - tache.debut).total_seconds() * 1000)
        tache = dataclasses.replace(tache, fin=fin, duree_ms=duree_ms, statut=statut, commentaire=commentaire)
        self.taches[tache_id] = tache
        return tache

    def lister(self, categorie: str | None = None, limite: int = 50) -> list[Tache]:
        resultat = [t for t in self.taches.values() if categorie is None or t.categorie == categorie]
        return sorted(resultat, key=lambda t: t.debut, reverse=True)[:limite]

    def get_derniere_par_nom(self, nom: str) -> Tache | None:
        candidats = sorted((t for t in self.taches.values() if t.nom == nom), key=lambda t: t.debut, reverse=True)
        return candidats[0] if candidats else None

    def compter_echecs_recents(self, depuis, categorie: str | None = None) -> int:
        return len([
            t for t in self.taches.values()
            if t.statut == "echec" and t.debut >= depuis and (categorie is None or t.categorie == categorie)
        ])


class FakeParametreRepository:
    def __init__(self) -> None:
        self._ids = _AutoId()
        self.parametres: dict[str, object] = {}  # keyed by cle

    def seed(self, parametre):
        if parametre.id is None:
            parametre = dataclasses.replace(parametre, id=self._ids.next())
        if parametre.date_modification is None:
            parametre = dataclasses.replace(parametre, date_modification=datetime.now(timezone.utc))
        self.parametres[parametre.cle] = parametre
        return parametre

    def lister(self):
        return sorted(self.parametres.values(), key=lambda p: p.cle)

    def get_parametre(self, cle: str):
        return self.parametres.get(cle)

    def update_parametre(self, cle: str, valeur: str):
        parametre = self.parametres.get(cle)
        if parametre is None:
            return None
        parametre = dataclasses.replace(parametre, valeur=valeur, date_modification=datetime.now(timezone.utc))
        self.parametres[cle] = parametre
        return parametre

    def obtenir_poids(self, prefixe: str) -> dict[str, float]:
        return {
            p.cle.removeprefix(f"{prefixe}."): float(p.valeur)
            for p in self.parametres.values()
            if p.cle.startswith(f"{prefixe}.")
        }


class FakeVersionRepository:
    def __init__(self) -> None:
        self._ids = _AutoId()
        self.versions: dict[int, object] = {}

    def creer(self, version):
        version = dataclasses.replace(version, id=self._ids.next(), date_publication=datetime.now(timezone.utc))
        self.versions[version.id] = version
        return version

    def lister(self, limite: int = 20):
        return sorted(self.versions.values(), key=lambda v: v.date_publication, reverse=True)[:limite]


class FakeCollecteService:
    """Remplace CollecteService dans les tests d'intégration — aucun accès réseau
    PMU (cf. L020 §2.2). `rapport` configurable par le test."""

    def __init__(self, rapport: RapportCollecte | None = None) -> None:
        self.rapport = rapport if rapport is not None else RapportCollecte()

    def collecter_programme_du_jour(self, jour):
        return self.rapport


class FakeControleRoiService:
    """Remplace ControleRoiService dans les tests d'intégration — `controles`
    configurable par le test (liste de `ControleRoi` déjà calculés)."""

    def __init__(self, controles: list | None = None) -> None:
        self.controles = controles if controles is not None else []

    def calculer_controles_manquants(self):
        return self.controles


class FakeSupervisionService:
    """Remplace SupervisionService — pas de connexion DB réelle ni de
    `shutil.disk_usage` en test ; `etat_configure` configurable par le test."""

    def __init__(self, etat: EtatSupervision | None = None) -> None:
        self.etat_configure = etat if etat is not None else EtatSupervision(
            base_de_donnees_ok=True, latence_db_ms=1.0, espace_disque_disponible_octets=1_000_000_000,
            taches_en_echec_24h=0, demarrage_processus=datetime.now(timezone.utc), uptime_secondes=1.0,
        )

    def etat(self) -> EtatSupervision:
        return self.etat_configure
