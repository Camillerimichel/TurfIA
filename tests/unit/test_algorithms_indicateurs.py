import pytest

from src.algorithms.indicateurs import (
    SCORE_NEUTRE_PAR_DEFAUT,
    calculer_indicateur_forme,
    calculer_indicateur_presse,
    calculer_indicateur_risque_taille_champ,
    calculer_indicateurs_marche,
    parser_musique,
)


def test_parser_musique_positions_simples():
    assert parser_musique("5p7p0p0p") == [5, 7, 10, 10]


def test_parser_musique_retire_les_marqueurs_annee():
    assert parser_musique("4p3p9p2p0p4p8p(25)6p9p") == [4, 3, 9, 2, 10, 4, 8, 6, 9]


def test_parser_musique_incident_non_numerique():
    assert parser_musique("Ap") == [10]


def test_parser_musique_absente():
    assert parser_musique(None) == []
    assert parser_musique("") == []


def test_calculer_indicateur_forme_premiere_place():
    assert calculer_indicateur_forme("1p") == 100.0


def test_calculer_indicateur_forme_absente_score_neutre():
    assert calculer_indicateur_forme(None) == SCORE_NEUTRE_PAR_DEFAUT


def test_calculer_indicateur_forme_moyenne_sur_n_courses():
    # positions [5,7,10,10] normalisées (1->100,10->0) : [55.56, 33.33, 0, 0], moyenne sur 3 dernières
    score = calculer_indicateur_forme("5p7p0p0p", nb_courses=3)
    assert score == pytest.approx((55.5555 + 33.3333 + 0) / 3, abs=0.01)


def test_calculer_indicateurs_marche_favori_recoit_le_meilleur_score():
    scores = calculer_indicateurs_marche([3.5, 8.0, 5.0])
    assert scores[0] == 100.0
    assert scores[1] == 0.0
    assert 0 < scores[2] < 100


def test_calculer_indicateurs_marche_cote_absente_recoit_score_neutre():
    scores = calculer_indicateurs_marche([3.5, None, 5.0])
    assert scores[1] == SCORE_NEUTRE_PAR_DEFAUT


def test_calculer_indicateurs_marche_toutes_cotes_absentes():
    assert calculer_indicateurs_marche([None, None]) == [SCORE_NEUTRE_PAR_DEFAUT, SCORE_NEUTRE_PAR_DEFAUT]


def test_calculer_indicateur_presse_premier_cite():
    assert calculer_indicateur_presse([15, 7, 4], numero_partant=15) == 100.0


def test_calculer_indicateur_presse_dernier_cite():
    # 3 chevaux cités, rang 3 (pire rang possible = 4, le non-cité) : 100*(3-1)/(4-1) inversé.
    assert calculer_indicateur_presse([15, 7, 4], numero_partant=4) == pytest.approx(33.333, abs=0.01)


def test_calculer_indicateur_presse_non_cite_recoit_le_pire_score():
    score_dernier_cite = calculer_indicateur_presse([15, 7, 4], numero_partant=4)
    score_non_cite = calculer_indicateur_presse([15, 7, 4], numero_partant=99)
    assert score_non_cite < score_dernier_cite
    assert score_non_cite == 0.0


def test_calculer_indicateur_risque_taille_champ_petit_champ():
    assert calculer_indicateur_risque_taille_champ(4) == 0.0


def test_calculer_indicateur_risque_taille_champ_grand_champ():
    assert calculer_indicateur_risque_taille_champ(20) == 100.0
