import json
import statistics

import pytest

from src.algorithms.rejeu import (
    agreger_par_hippodrome,
    agreger_par_tranche_score,
    agreger_par_type_pari,
    agreger_resultats_rejeu,
    calculer_drawdown,
    calculer_stabilite,
    serialiser_liste_stats,
)
from src.models.statistique import StatistiqueHippodrome, StatistiqueScore


def test_agreger_resultats_rejeu_vide():
    assert agreger_resultats_rejeu([]) == (0, None, None)


def test_agreger_resultats_rejeu_tout_gagnant():
    resultats = [(10.0, 14.0, True), (5.0, 8.0, True)]
    nb_paris, roi, taux_reussite = agreger_resultats_rejeu(resultats)
    assert nb_paris == 2
    assert roi == pytest.approx(((14.0 + 8.0 - 15.0) / 15.0) * 100)
    assert taux_reussite == 100.0


def test_agreger_resultats_rejeu_tout_perdant():
    resultats = [(10.0, 0.0, False), (5.0, 0.0, False)]
    nb_paris, roi, taux_reussite = agreger_resultats_rejeu(resultats)
    assert nb_paris == 2
    assert roi == pytest.approx(-100.0)
    assert taux_reussite == 0.0


def test_agreger_resultats_rejeu_mixte():
    resultats = [(10.0, 14.0, True), (10.0, 0.0, False), (10.0, 0.0, False), (10.0, 0.0, False)]
    nb_paris, roi, taux_reussite = agreger_resultats_rejeu(resultats)
    assert nb_paris == 4
    assert roi == pytest.approx(((14.0 - 40.0) / 40.0) * 100)
    assert taux_reussite == 25.0


def test_agreger_par_tranche_score_vide():
    assert agreger_par_tranche_score([]) == []


def test_agreger_par_tranche_score_omet_les_tranches_sans_course():
    resultats = agreger_par_tranche_score([(50.0, 10.0, 14.0)])
    assert len(resultats) == 1
    assert resultats[0].score_min == 0.0
    assert resultats[0].score_max == 60.0
    assert resultats[0].nb_courses == 1
    assert resultats[0].nb_gagnantes == 1
    assert resultats[0].roi == pytest.approx(40.0)
    assert resultats[0].taux_reussite == 100.0


def test_agreger_par_tranche_score_borne_basse_incluse_haute_exclue():
    # 60.0 pile sur la borne -> tranche [60,75), pas [0,60)
    resultats = agreger_par_tranche_score([(60.0, 10.0, 0.0)])
    assert len(resultats) == 1
    assert (resultats[0].score_min, resultats[0].score_max) == (60.0, 75.0)


def test_agreger_par_tranche_score_derniere_tranche_borne_haute_incluse():
    resultats = agreger_par_tranche_score([(100.0, 10.0, 20.0)])
    assert len(resultats) == 1
    assert (resultats[0].score_min, resultats[0].score_max) == (85.0, 100.0)


def test_agreger_par_tranche_score_au_dela_de_100_est_omis():
    # Garde-fou défensif : ne devrait plus se produire depuis que
    # calculer_score_final borne son résultat à [0, 100] (2026-07-11), mais
    # une entrée hors bornes (ex. donnée historique) reste omise, pas plantée.
    assert agreger_par_tranche_score([(102.5, 10.0, 20.0)]) == []


def test_agreger_par_tranche_score_plusieurs_courses_meme_tranche():
    resultats = agreger_par_tranche_score([(90.0, 10.0, 20.0), (95.0, 10.0, 0.0)])
    assert len(resultats) == 1
    assert resultats[0].nb_courses == 2
    assert resultats[0].nb_gagnantes == 1
    assert resultats[0].taux_reussite == 50.0
    assert resultats[0].roi == pytest.approx(((20.0 - 20.0) / 20.0) * 100)


def test_agreger_par_hippodrome_vide():
    assert agreger_par_hippodrome([]) == []


def test_agreger_par_hippodrome_regroupe_par_id():
    resultats = agreger_par_hippodrome([(1, 10.0, 20.0), (1, 10.0, 0.0), (2, 5.0, 5.0)])
    par_id = {r.hippodrome_id: r for r in resultats}
    assert par_id[1].nb_courses == 2
    assert par_id[1].mises == 20.0
    assert par_id[1].gains == 20.0
    assert par_id[1].profit == 0.0
    assert par_id[2].nb_courses == 1
    assert par_id[2].roi == pytest.approx(0.0)


def test_agreger_par_type_pari_vide():
    assert agreger_par_type_pari([]) == []


def test_agreger_par_type_pari_regroupe_par_type():
    resultats = agreger_par_type_pari(
        [("Simple Gagnant", 10.0, 14.0), ("Simple Gagnant", 10.0, 0.0), ("Couplé Gagnant", 1.0, 67.60)]
    )
    par_type = {r.type_pari: r for r in resultats}
    assert par_type["Simple Gagnant"].nb_paris == 2
    assert par_type["Simple Gagnant"].taux_reussite == 50.0
    assert par_type["Couplé Gagnant"].nb_paris == 1
    assert par_type["Couplé Gagnant"].roi == pytest.approx(((67.60 - 1.0) / 1.0) * 100)


def test_calculer_drawdown_vide():
    assert calculer_drawdown([]) is None


def test_calculer_drawdown_toujours_positif_est_nul():
    assert calculer_drawdown([10.0, 5.0, 20.0]) == 0.0


def test_calculer_drawdown_pic_puis_creux():
    # cumul : 100, 60 (baisse de 40 depuis le pic 100), 90 (remonte, toujours -10 vs pic)
    assert calculer_drawdown([100.0, -40.0, 30.0]) == 40.0


def test_calculer_drawdown_pire_baisse_apres_remontee_partielle():
    # cumul : 100 (pic), 80 (-20), 110 (nouveau pic), 50 (-60, pire baisse)
    assert calculer_drawdown([100.0, -20.0, 30.0, -60.0]) == 60.0


def test_calculer_stabilite_vide():
    assert calculer_stabilite([]) is None


def test_calculer_stabilite_roi_constant_est_nulle():
    assert calculer_stabilite([10.0, 10.0, 10.0]) == 0.0


def test_calculer_stabilite_roi_variable():
    valeurs = [10.0, -20.0, 30.0]
    assert calculer_stabilite(valeurs) == pytest.approx(statistics.pstdev(valeurs), abs=0.01)


def test_serialiser_liste_stats_vide():
    assert serialiser_liste_stats([]) == "[]"


def test_serialiser_liste_stats_contenu_reconstructible():
    objets = [
        StatistiqueScore(score_min=0.0, score_max=60.0, nb_courses=1, nb_gagnantes=1, roi=40.0, taux_reussite=100.0),
        StatistiqueHippodrome(hippodrome_id=1, nb_courses=2, mises=20.0, gains=20.0, profit=0.0, roi=0.0),
    ]
    resultat = json.loads(serialiser_liste_stats(objets))
    assert len(resultat) == 2
    assert resultat[0]["score_min"] == 0.0
    assert resultat[1]["hippodrome_id"] == 1
