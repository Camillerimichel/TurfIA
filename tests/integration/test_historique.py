"""Tests d'intégration du module Historique (L018 §8) — recherche transversale
en lecture seule, sans base réelle (cf. tests/integration/fakes.py)."""


def _creer_course_avec_analyse_et_pari(client, decision="Jeu normal"):
    reunion = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1}
    ).json()["data"]
    course = client.post(
        f"/api/v1/reunions/{reunion['id']}/courses", json={"numero": 1, "nom": "Prix Test"}
    ).json()["data"]
    cheval = client.post("/api/v1/chevaux", json={"nom": "Cheval Test"}).json()["data"]
    partant = client.post(
        f"/api/v1/courses/{course['id']}/partants", json={"cheval_id": cheval["id"], "numero": 1}
    ).json()["data"]

    detail = client.post(
        f"/api/v1/courses/{course['id']}/analyses",
        json={
            "partants": [{"partant_id": partant["id"], "sous_scores": {"marche": 90}, "cote": 3.0}],
            "sous_risques_course": {"marche": 20},
            "mise_reference": 10,
        },
    ).json()["data"]
    return reunion, course, detail


def test_historique_sans_filtre_retourne_les_lignes(client):
    reunion, course, detail = _creer_course_avec_analyse_et_pari(client)

    reponse = client.get("/api/v1/historique")

    assert reponse.status_code == 200
    lignes = reponse.json()["data"]
    assert len(lignes) >= 1
    ligne = next(l for l in lignes if l["analyse_id"] == detail["analyse"]["id"])
    assert ligne["course_id"] == course["id"]
    assert ligne["hippodrome_id"] == reunion["hippodrome_id"]


def test_historique_filtre_par_hippodrome_inconnu_est_vide(client):
    _creer_course_avec_analyse_et_pari(client)

    reponse = client.get("/api/v1/historique", params={"hippodrome_id": 999})

    assert reponse.status_code == 200
    assert reponse.json()["data"] == []


def test_historique_filtre_par_date(client):
    _creer_course_avec_analyse_et_pari(client)

    reponse = client.get("/api/v1/historique", params={"date_debut": "2026-01-01", "date_fin": "2026-01-31"})

    assert reponse.status_code == 200
    assert reponse.json()["data"] == []


def test_historique_filtre_par_type_pari(client):
    _, _, detail = _creer_course_avec_analyse_et_pari(client)
    type_pari_attendu = detail["paris"][0]["type_pari"] if detail["paris"] else None

    reponse = client.get("/api/v1/historique", params={"type_pari": "Type inexistant"})
    assert reponse.json()["data"] == []

    if type_pari_attendu is not None:
        reponse = client.get("/api/v1/historique", params={"type_pari": type_pari_attendu})
        assert len(reponse.json()["data"]) >= 1
