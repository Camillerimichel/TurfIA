"""Tests d'intégration des endpoints /statistiques/* — lecture seule (cf. plan
Module Statistiques). Les tables sont alimentées uniquement par
`scripts/calculer_statistiques.py`, jamais via l'API.
"""

from datetime import date

from src.models.statistique import StatistiqueGlobale, StatistiqueGlobaleJour, StatistiqueHippodrome, StatistiqueScore


def test_globale_par_jour_vide_par_defaut(client):
    """Cf. retour utilisateur 2026-07-12 : tableau "Globale" segmenté par jour
    + consolidation totale, calculé à la demande (jamais persisté)."""
    reponse = client.get("/api/v1/statistiques/globale/jours")
    assert reponse.status_code == 200
    corps = reponse.json()["data"]
    assert corps["jours"] == []
    # Le total reste l'agrégat de `calculer_globale()` — zéro par défaut, pas absent.
    assert corps["total"]["nb_courses"] == 0
    assert corps["total"]["roi"] is None


def test_globale_par_jour_retourne_le_detail_et_le_total(client, repos):
    repos["statistiques"].a_calculer_globale_par_jour = [
        StatistiqueGlobaleJour(
            jour=date(2026, 7, 12), nb_courses=3, nb_jouees=2, nb_ignorees=1,
            mises=20.0, gains=14.0, profit=-6.0, roi=-30.0, taux_reussite=50.0,
        ),
        StatistiqueGlobaleJour(
            jour=date(2026, 7, 11), nb_courses=2, nb_jouees=1, nb_ignorees=1,
            mises=10.0, gains=25.0, profit=15.0, roi=150.0, taux_reussite=100.0,
        ),
    ]
    repos["statistiques"].a_calculer_globale = StatistiqueGlobale(
        nb_courses=5, nb_jouees=3, nb_ignorees=2, mises=30.0, gains=39.0, profit=9.0, roi=30.0, taux_reussite=66.67,
    )

    reponse = client.get("/api/v1/statistiques/globale/jours")
    assert reponse.status_code == 200
    corps = reponse.json()["data"]
    assert [j["jour"] for j in corps["jours"]] == ["2026-07-12", "2026-07-11"]
    assert corps["jours"][0]["profit"] == -6.0
    assert corps["total"]["nb_courses"] == 5
    assert corps["total"]["profit"] == 9.0
    assert "jour" not in corps["total"]


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


def test_list_globale_ne_montre_que_le_dernier_calcul():
    """Non-régression : cf. PROJECT_STATE.md — chaque recalcul horaire (L033)
    insère une nouvelle ligne sans jamais remplacer l'ancienne (L030.4 §10),
    mais l'API ne doit renvoyer que la plus récente, pas la pile de chaque
    passage horaire ("je ne comprends rien", retour utilisateur)."""
    from tests.integration.fakes import FakeStatistiqueRepository

    repo = FakeStatistiqueRepository()
    repo.create_globale(StatistiqueGlobale(nb_courses=3, nb_jouees=1, nb_ignorees=2, mises=10.0, gains=5.0, profit=-5.0, roi=-50.0))
    repo.create_globale(StatistiqueGlobale(nb_courses=5, nb_jouees=2, nb_ignorees=3, mises=20.0, gains=25.0, profit=5.0, roi=25.0))

    lignes = repo.list_globale()

    assert len(lignes) == 1
    assert lignes[0].nb_courses == 5
    assert lignes[0].roi == 25.0


def test_list_hippodromes(client, repos):
    repos["statistiques"].create_hippodrome(
        StatistiqueHippodrome(hippodrome_id=1, nb_courses=2, mises=20.0, gains=14.0, profit=-6.0, roi=-30.0)
    )
    reponse = client.get("/api/v1/statistiques/hippodromes")
    assert reponse.status_code == 200
    assert reponse.json()["data"][0]["hippodrome_id"] == 1


def test_list_hippodromes_ne_montre_que_le_dernier_calcul_par_hippodrome():
    from tests.integration.fakes import FakeStatistiqueRepository

    repo = FakeStatistiqueRepository()
    repo.create_hippodrome(StatistiqueHippodrome(hippodrome_id=1, nb_courses=2, mises=20.0, gains=14.0, profit=-6.0, roi=-30.0))
    repo.create_hippodrome(StatistiqueHippodrome(hippodrome_id=2, nb_courses=1, mises=10.0, gains=8.0, profit=-2.0, roi=-20.0))
    # Deuxième recalcul pour l'hippodrome 1 (plus de courses accumulées) : doit remplacer le premier à l'affichage.
    repo.create_hippodrome(StatistiqueHippodrome(hippodrome_id=1, nb_courses=6, mises=60.0, gains=70.0, profit=10.0, roi=16.67))

    lignes = repo.list_hippodromes()

    assert len(lignes) == 2  # une par hippodrome distinct, pas 3
    par_hippodrome = {l.hippodrome_id: l for l in lignes}
    assert par_hippodrome[1].nb_courses == 6  # le second calcul, pas le premier
    assert par_hippodrome[2].nb_courses == 1


def test_list_scores_disciplines_paris_modeles_vides_par_defaut(client):
    for chemin in ("scores", "disciplines", "paris", "modeles"):
        reponse = client.get(f"/api/v1/statistiques/{chemin}")
        assert reponse.status_code == 200
        assert reponse.json()["data"] == []


def test_list_scores_ne_montre_que_le_dernier_calcul_par_tranche():
    from tests.integration.fakes import FakeStatistiqueRepository

    repo = FakeStatistiqueRepository()
    repo.create_score(StatistiqueScore(score_min=0.0, score_max=60.0, nb_courses=5, nb_gagnantes=0, roi=None, taux_reussite=0.0))
    repo.create_score(StatistiqueScore(score_min=0.0, score_max=60.0, nb_courses=9, nb_gagnantes=0, roi=None, taux_reussite=0.0))

    lignes = repo.list_scores()

    assert len(lignes) == 1
    assert lignes[0].nb_courses == 9
