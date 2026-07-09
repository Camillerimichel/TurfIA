"""Teste AnalyseService avec un repository en mémoire (cf. tests/integration/
fakes.py) — en particulier `persister=False`, nécessaire au moteur de rejeu
(cf. scripts/rejouer_versions.py, L031.7 §4) : les paris doivent être
construits en mémoire même sans écriture en base.
"""

from src.services.analyse_service import AnalyseService, DonneesPartant
from tests.integration.fakes import FakeAnalyseRepository

PARTANTS = [
    DonneesPartant(partant_id=1, sous_scores={"marche": 90, "presse": 85}, cote=2.5),
    DonneesPartant(partant_id=2, sous_scores={"marche": 60, "presse": 55}, cote=6.0),
    DonneesPartant(partant_id=3, sous_scores={"marche": 55, "presse": 50}, cote=8.0),
]
SOUS_RISQUES = {"marche": 20, "presse": 15}


def test_persister_false_ne_persiste_rien():
    repo = FakeAnalyseRepository()
    resultat = AnalyseService(repo).analyser_course(
        course_id=1, version=1, partants=PARTANTS, sous_risques_course=SOUS_RISQUES, persister=False
    )
    assert resultat.analyse.id is None
    assert repo.analyses == {}
    assert repo.paris == {}


def test_persister_false_construit_quand_meme_les_paris_en_memoire():
    repo = FakeAnalyseRepository()
    resultat = AnalyseService(repo).analyser_course(
        course_id=1, version=1, partants=PARTANTS, sous_risques_course=SOUS_RISQUES, persister=False
    )
    assert len(resultat.paris) > 0
    for pari in resultat.paris:
        assert pari.id is None
        assert pari.combinaison is not None


def test_persister_true_persiste_les_memes_paris():
    repo = FakeAnalyseRepository()
    resultat = AnalyseService(repo).analyser_course(
        course_id=1, version=1, partants=PARTANTS, sous_risques_course=SOUS_RISQUES, persister=True
    )
    assert resultat.analyse.id is not None
    assert len(resultat.paris) > 0
    for pari in resultat.paris:
        assert pari.id is not None
