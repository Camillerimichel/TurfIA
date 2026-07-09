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


class _AutoId:
    def __init__(self) -> None:
        self._counter = itertools.count(1)

    def next(self) -> int:
        return next(self._counter)


class FakeReferentielRepository:
    def __init__(self) -> None:
        self._ids = _AutoId()
        self.hippodromes: dict[int, object] = {}

    def seed_hippodrome(self, hippodrome) -> object:
        hippodrome = dataclasses.replace(hippodrome, id=self._ids.next())
        self.hippodromes[hippodrome.id] = hippodrome
        return hippodrome

    def get_hippodrome(self, hippodrome_id: int):
        return self.hippodromes.get(hippodrome_id)

    def list_hippodromes(self):
        return list(self.hippodromes.values())


class FakeCourseRepository:
    def __init__(self) -> None:
        self._ids = _AutoId()
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
        self.performances_hippodrome: dict[tuple[int, int], tuple[int, int]] = {}
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

    def get_reunion(self, reunion_id: int):
        return self.reunions.get(reunion_id)

    def update_reunion(self, reunion_id: int, champs: dict):
        return self._appliquer_patch(self.reunions, reunion_id, champs)

    def delete_reunion(self, reunion_id: int) -> bool:
        references = any(c.reunion_id == reunion_id for c in self.courses.values())
        return self._supprimer(self.reunions, reunion_id, "la réunion", references)

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

    def list_partants_by_course(self, course_id: int):
        return [p for p in self.partants.values() if p.course_id == course_id]

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

    def compter_performances_cheval_hippodrome(
        self, cheval_id: int, hippodrome_id: int, exclure_course_id: int
    ) -> tuple[int, int]:
        return self.performances_hippodrome.get((cheval_id, hippodrome_id), (0, 0))

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
        analyse = dataclasses.replace(analyse, id=self._ids.next())
        self.analyses[analyse.id] = analyse
        self.analyse_partants[analyse.id] = []
        self.selections[analyse.id] = []
        self.paris[analyse.id] = []
        return analyse

    def get_analyse(self, analyse_id: int):
        return self.analyses.get(analyse_id)

    def list_analyses_by_course(self, course_id: int):
        return [a for a in self.analyses.values() if a.course_id == course_id]

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
    réponse brute simulée de /rapports-definitifs."""

    def __init__(self, rapports_par_course: dict | None = None) -> None:
        self.rapports_par_course = rapports_par_course or {}

    def recuperer_rapports_definitifs(self, jour, num_reunion: int, num_course: int) -> list[dict]:
        cle = (num_reunion, num_course)
        if cle not in self.rapports_par_course:
            raise ImportationError(f"Rapports non disponibles pour R{num_reunion}C{num_course} (simulé).")
        return self.rapports_par_course[cle]


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
