"""Repositories en mémoire pour les tests d'intégration API (sans base réelle).

Implémentent la même interface que les repositories SQL (cf. src/repositories/),
ce qui permet de tester le câblage FastAPI (routes -> schémas -> dépendances ->
gestion d'erreurs) sans dépendre d'une instance PostgreSQL (cf. L020 §5.2).
"""

from __future__ import annotations

import dataclasses
import itertools
from datetime import datetime, timezone


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

    def create_reunion(self, reunion):
        reunion = dataclasses.replace(reunion, id=self._ids.next())
        self.reunions[reunion.id] = reunion
        return reunion

    def get_reunion(self, reunion_id: int):
        return self.reunions.get(reunion_id)

    def update_reunion(self, reunion_id: int, champs: dict):
        return self._appliquer_patch(self.reunions, reunion_id, champs)

    def create_course(self, course):
        course = dataclasses.replace(course, id=self._ids.next())
        self.courses[course.id] = course
        return course

    def get_course(self, course_id: int):
        return self.courses.get(course_id)

    def update_course(self, course_id: int, champs: dict):
        return self._appliquer_patch(self.courses, course_id, champs)

    def list_courses_by_reunion(self, reunion_id: int):
        return [c for c in self.courses.values() if c.reunion_id == reunion_id]

    def create_cheval(self, cheval):
        cheval = dataclasses.replace(cheval, id=self._ids.next())
        self.chevaux[cheval.id] = cheval
        return cheval

    def get_cheval(self, cheval_id: int):
        return self.chevaux.get(cheval_id)

    def update_cheval(self, cheval_id: int, champs: dict):
        return self._appliquer_patch(self.chevaux, cheval_id, champs)

    def create_jockey(self, jockey):
        jockey = dataclasses.replace(jockey, id=self._ids.next())
        self.jockeys[jockey.id] = jockey
        return jockey

    def get_jockey(self, jockey_id: int):
        return self.jockeys.get(jockey_id)

    def update_jockey(self, jockey_id: int, champs: dict):
        return self._appliquer_patch(self.jockeys, jockey_id, champs)

    def create_entraineur(self, entraineur):
        entraineur = dataclasses.replace(entraineur, id=self._ids.next())
        self.entraineurs[entraineur.id] = entraineur
        return entraineur

    def get_entraineur(self, entraineur_id: int):
        return self.entraineurs.get(entraineur_id)

    def update_entraineur(self, entraineur_id: int, champs: dict):
        return self._appliquer_patch(self.entraineurs, entraineur_id, champs)

    def create_partant(self, partant):
        partant = dataclasses.replace(partant, id=self._ids.next())
        self.partants[partant.id] = partant
        return partant

    def get_partant(self, partant_id: int):
        return self.partants.get(partant_id)

    def update_partant(self, partant_id: int, champs: dict):
        return self._appliquer_patch(self.partants, partant_id, champs)

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
        self.entrees: list[tuple] = []

    def enregistrer(self, utilisateur_id, action: str, objet: str | None = None) -> None:
        self.entrees.append((utilisateur_id, action, objet))

    def create_controle_roi(self, controle):
        return dataclasses.replace(controle, id=self._ids.next())


class FakeConsensusPresseService:
    """Remplace ConsensusPresseService dans les tests d'intégration — aucun accès
    réseau (cf. L020 §2.2). `classement` est configurable par le test."""

    def __init__(self, classement: list[int] | None = None) -> None:
        self.classement = classement

    def recuperer_classement_presse(self, numero_reunion: int, numero_course: int) -> list[int] | None:
        return self.classement
