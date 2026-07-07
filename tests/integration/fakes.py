"""Repositories en mémoire pour les tests d'intégration API (sans base réelle).

Implémentent la même interface que les repositories SQL (cf. src/repositories/),
ce qui permet de tester le câblage FastAPI (routes -> schémas -> dépendances ->
gestion d'erreurs) sans dépendre d'une instance PostgreSQL (cf. L020 §5.2).
"""

from __future__ import annotations

import dataclasses
import itertools


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

    def create_reunion(self, reunion):
        reunion = dataclasses.replace(reunion, id=self._ids.next())
        self.reunions[reunion.id] = reunion
        return reunion

    def get_reunion(self, reunion_id: int):
        return self.reunions.get(reunion_id)

    def create_course(self, course):
        course = dataclasses.replace(course, id=self._ids.next())
        self.courses[course.id] = course
        return course

    def get_course(self, course_id: int):
        return self.courses.get(course_id)

    def list_courses_by_reunion(self, reunion_id: int):
        return [c for c in self.courses.values() if c.reunion_id == reunion_id]

    def create_cheval(self, cheval):
        cheval = dataclasses.replace(cheval, id=self._ids.next())
        self.chevaux[cheval.id] = cheval
        return cheval

    def get_cheval(self, cheval_id: int):
        return self.chevaux.get(cheval_id)

    def create_jockey(self, jockey):
        jockey = dataclasses.replace(jockey, id=self._ids.next())
        self.jockeys[jockey.id] = jockey
        return jockey

    def get_jockey(self, jockey_id: int):
        return self.jockeys.get(jockey_id)

    def create_entraineur(self, entraineur):
        entraineur = dataclasses.replace(entraineur, id=self._ids.next())
        self.entraineurs[entraineur.id] = entraineur
        return entraineur

    def get_entraineur(self, entraineur_id: int):
        return self.entraineurs.get(entraineur_id)

    def create_partant(self, partant):
        partant = dataclasses.replace(partant, id=self._ids.next())
        self.partants[partant.id] = partant
        return partant

    def list_partants_by_course(self, course_id: int):
        return [p for p in self.partants.values() if p.course_id == course_id]

    def create_cote(self, cote):
        self.cotes[cote.partant_id] = cote.cote
        return dataclasses.replace(cote, id=self._ids.next())

    def get_dernieres_cotes_par_course(self, course_id: int) -> dict[int, float]:
        return {p.id: self.cotes[p.id] for p in self.list_partants_by_course(course_id) if p.id in self.cotes}


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

    def create_controle_roi(self, controle):
        return dataclasses.replace(controle, id=self._ids.next())
