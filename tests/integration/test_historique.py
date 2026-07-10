"""Tests d'intégration du module Historique (L018 §8) — recherche transversale
en lecture seule, sans base réelle (cf. tests/integration/fakes.py)."""


def _creer_course_avec_analyse_et_pari(client, decision="Jeu normal", version=1):
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
            "version": version,
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
    assert ligne["date_calcul"] == detail["analyse"]["date_calcul"]


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


def test_historique_ne_montre_que_la_derniere_version_par_course(client):
    """Non-régression : une course réanalysée plusieurs fois (cf. L033,
    automatisation horaire à version croissante) ne doit apparaître qu'une
    seule fois dans l'historique, avec la version la plus récente — pas une
    ligne par version calculée dans la journée."""
    reunion, course, detail_v1 = _creer_course_avec_analyse_et_pari(client, version=1)
    partant_id = int(detail_v1["paris"][0]["combinaison"]) if detail_v1["paris"] else None
    reponse_v2 = client.post(
        f"/api/v1/courses/{course['id']}/analyses",
        json={
            "version": 2,
            "partants": [{"partant_id": partant_id, "sous_scores": {"marche": 90}, "cote": 3.0}],
            "sous_risques_course": {"marche": 20},
            "mise_reference": 10,
        },
    )
    assert reponse_v2.status_code == 201
    detail_v2 = reponse_v2.json()["data"]

    reponse = client.get("/api/v1/historique")

    assert reponse.status_code == 200
    lignes = [l for l in reponse.json()["data"] if l["course_id"] == course["id"]]
    assert len(lignes) >= 1
    # Toutes les lignes de cette course viennent de la même (dernière) analyse —
    # peu importe qu'elle ait plusieurs paris (plusieurs lignes légitimes),
    # jamais un mélange de versions différentes.
    assert {l["analyse_id"] for l in lignes} == {detail_v2["analyse"]["id"]}
    assert {l["version"] for l in lignes} == {2}


def test_historique_filtre_decisions_ou_logique(client):
    """cf. accueil.js : un filtre à choix multiples est une condition "ou"."""
    _, course_normal, detail = _creer_course_avec_analyse_et_pari(client)
    decision_reelle = detail["analyse"]["decision"]

    reponse = client.get("/api/v1/historique", params={"decisions": [decision_reelle, "Décision inexistante"]})
    assert reponse.status_code == 200
    assert any(l["course_id"] == course_normal["id"] for l in reponse.json()["data"])

    reponse_vide = client.get("/api/v1/historique", params={"decisions": ["Décision inexistante"]})
    assert reponse_vide.json()["data"] == []
