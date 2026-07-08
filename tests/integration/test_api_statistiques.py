"""Tests d'intégration des endpoints /statistiques/* — lecture seule (cf. plan
Module Statistiques). Les tables sont alimentées uniquement par
`scripts/calculer_statistiques.py`, jamais via l'API.
"""

from src.models.statistique import StatistiqueGlobale, StatistiqueHippodrome


def test_list_globale_vide_par_defaut(client):
    reponse = client.get("/api/v1/statistiques/globale")
    assert reponse.status_code == 200
    assert reponse.json()["data"] == []


def test_list_globale_retourne_les_lignes_persistees(client, repos):
    repos["statistiques"].create_globale(
        StatistiqueGlobale(nb_courses=3, nb_jouees=2, nb_ignorees=1, mises=20.0, gains=14.0, profit=-6.0, roi=-30.0)
    )
    reponse = client.get("/api/v1/statistiques/globale")
    assert reponse.status_code == 200
    corps = reponse.json()["data"]
    assert len(corps) == 1
    assert corps[0]["nb_courses"] == 3
    assert corps[0]["roi"] == -30.0


def test_list_hippodromes(client, repos):
    repos["statistiques"].create_hippodrome(
        StatistiqueHippodrome(hippodrome_id=1, nb_courses=2, mises=20.0, gains=14.0, profit=-6.0, roi=-30.0)
    )
    reponse = client.get("/api/v1/statistiques/hippodromes")
    assert reponse.status_code == 200
    assert reponse.json()["data"][0]["hippodrome_id"] == 1


def test_list_scores_disciplines_paris_modeles_vides_par_defaut(client):
    for chemin in ("scores", "disciplines", "paris", "modeles"):
        reponse = client.get(f"/api/v1/statistiques/{chemin}")
        assert reponse.status_code == 200
        assert reponse.json()["data"] == []
