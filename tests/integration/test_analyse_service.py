"""Teste AnalyseService avec un repository en mémoire (cf. tests/integration/
fakes.py) — en particulier `persister=False`, nécessaire au moteur de rejeu
(cf. scripts/rejouer_versions.py, L031.7 §4) : les paris doivent être
construits en mémoire même sans écriture en base.
"""

import pytest

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


def test_commentaire_et_source_sont_persistes():
    """Cf. IaAnalyseService (retour utilisateur 2026-07-12) : la synthèse IA et
    l'origine ('manuel'/'ia') doivent être persistées telles quelles."""
    repo = FakeAnalyseRepository()
    resultat = AnalyseService(repo).analyser_course(
        course_id=1, version=1, partants=PARTANTS, sous_risques_course=SOUS_RISQUES,
        commentaire="Synthèse IA de test.", source="ia",
    )
    assert resultat.analyse.commentaire == "Synthèse IA de test."
    assert resultat.analyse.source == "ia"
    persiste = repo.get_analyse(resultat.analyse.id)
    assert persiste.commentaire == "Synthèse IA de test."
    assert persiste.source == "ia"


def test_commentaire_et_source_ont_des_defauts_retrocompatibles():
    repo = FakeAnalyseRepository()
    resultat = AnalyseService(repo).analyser_course(
        course_id=1, version=1, partants=PARTANTS, sous_risques_course=SOUS_RISQUES
    )
    assert resultat.analyse.commentaire is None
    assert resultat.analyse.source == "manuel"


def test_roi_theorique_independant_de_la_mise_reference():
    """Non-régression : le ROI théorique (un pourcentage) ne doit pas dépendre
    de la mise de référence utilisée pour le calcul — bug réel corrigé (cf.
    PROJECT_STATE.md) où `rapport_estime` valait la cote brute au lieu de
    `mise_reference * cote` (le gain total attendu, cf. L031.4 §5), ce qui
    faisait dépendre le ROI de la mise choisie et le rendait presque toujours
    proche de -100 % en pratique (mise_reference=10 très supérieure au
    "probabilité × cote" typique)."""
    rois_par_mise = {}
    for mise_reference in (10.0, 25.0, 100.0):
        resultat = AnalyseService(FakeAnalyseRepository()).analyser_course(
            course_id=1, version=1, partants=PARTANTS, sous_risques_course=SOUS_RISQUES,
            mise_reference=mise_reference, persister=False,
        )
        rois_par_mise[mise_reference] = {pc.partant_id: pc.roi_theorique for pc in resultat.partants_classes}

    assert rois_par_mise[10.0] == pytest.approx(rois_par_mise[25.0])
    assert rois_par_mise[10.0] == pytest.approx(rois_par_mise[100.0])
    # Signature du bug corrigé : un favori raisonnable (cote 2.5) affichait un
    # ROI toujours proche de -100 %, quelle que soit sa vraie valeur.
    assert rois_par_mise[10.0][1] > -50
