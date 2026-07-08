"""Teste l'orchestration de StatistiqueService avec un repository en mémoire (cf.
tests/integration/fakes.py) — l'exactitude de l'agrégation SQL elle-même a été
vérifiée contre une instance PostgreSQL réelle (cf. PROJECT_STATE.md)."""

from src.models.statistique import (
    StatistiqueDiscipline,
    StatistiqueGlobale,
    StatistiqueHippodrome,
    StatistiqueModele,
    StatistiquePari,
    StatistiqueScore,
)
from src.services.statistique_service import StatistiqueService
from tests.integration.fakes import FakeStatistiqueRepository


def test_calculer_toutes_persiste_les_6_tables():
    repo = FakeStatistiqueRepository()
    repo.a_calculer_globale = StatistiqueGlobale(nb_courses=1, nb_jouees=1, mises=10.0, gains=14.0)
    repo.a_calculer_scores = [StatistiqueScore(score_min=85.0, score_max=100.0, nb_courses=1, nb_gagnantes=1)]
    repo.a_calculer_hippodromes = [StatistiqueHippodrome(hippodrome_id=1, nb_courses=1)]
    repo.a_calculer_disciplines = [StatistiqueDiscipline(discipline_id=1, nb_courses=1)]
    repo.a_calculer_paris = [StatistiquePari(type_pari="Simple Gagnant", nb_paris=1)]
    repo.a_calculer_modeles = [StatistiqueModele(version_modele="1", nb_courses=1)]

    resume = StatistiqueService(repo).calculer_toutes()

    assert resume == {"globale": 1, "scores": 1, "hippodromes": 1, "disciplines": 1, "paris": 1, "modeles": 1}
    assert len(repo.globale) == 1
    assert repo.globale[0].id is not None  # persisté (id assigné), jamais mis à jour en place
    assert len(repo.scores) == 1
    assert len(repo.hippodromes) == 1
    assert len(repo.disciplines) == 1
    assert len(repo.paris) == 1
    assert len(repo.modeles) == 1


def test_calculer_toutes_avec_plusieurs_tranches_de_score():
    repo = FakeStatistiqueRepository()
    repo.a_calculer_globale = StatistiqueGlobale()
    repo.a_calculer_scores = [
        StatistiqueScore(score_min=0.0, score_max=60.0, nb_courses=1, nb_gagnantes=0),
        StatistiqueScore(score_min=85.0, score_max=100.0, nb_courses=1, nb_gagnantes=1),
    ]

    resume = StatistiqueService(repo).calculer_toutes()

    assert resume["scores"] == 2
    assert len(repo.scores) == 2
