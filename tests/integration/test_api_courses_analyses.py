"""Tests d'intégration API — cf. L020 §5 (API <-> Services), sans base réelle
(repositories simulés, cf. tests/integration/fakes.py).
"""


def test_flux_complet_creation_et_analyse(client):
    reunion = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1}
    ).json()["data"]
    assert reunion["id"] == 1

    course = client.post(
        f"/api/v1/reunions/{reunion['id']}/courses",
        json={"numero": 1, "nom": "Prix Test"},
    ).json()["data"]
    assert course["reunion_id"] == reunion["id"]

    partants = []
    for nom, cote, scores in [
        ("Cheval A", 3.5, {"marche": 80, "presse": 70}),
        ("Cheval B", 8.0, {"marche": 50, "presse": 55}),
        ("Cheval C", 5.0, {"marche": 60, "presse": 65}),
    ]:
        cheval = client.post("/api/v1/chevaux", json={"nom": nom}).json()["data"]
        partant = client.post(
            f"/api/v1/courses/{course['id']}/partants",
            json={"cheval_id": cheval["id"], "numero": len(partants) + 1},
        ).json()["data"]
        partants.append((partant, cote, scores))

    reponse_analyse = client.post(
        f"/api/v1/courses/{course['id']}/analyses",
        json={
            "partants": [
                {"partant_id": p["id"], "sous_scores": scores, "cote": cote}
                for p, cote, scores in partants
            ],
            "sous_risques_course": {"marche": 30, "presse": 20},
        },
    )
    assert reponse_analyse.status_code == 201
    detail = reponse_analyse.json()["data"]
    assert detail["analyse"]["course_id"] == course["id"]
    assert len(detail["partants"]) == 3
    assert {p["rang"] for p in detail["partants"]} == {1, 2, 3}

    relecture = client.get(f"/api/v1/analyses/{detail['analyse']['id']}")
    assert relecture.status_code == 200
    detail_relu = relecture.json()["data"]
    assert detail_relu["analyse"]["id"] == detail["analyse"]["id"]
    assert len(detail_relu["partants"]) == 3


def test_enveloppe_de_reponse_normalisee(client):
    reponse = client.get("/api/v1/system/health")
    corps = reponse.json()
    assert corps["success"] is True
    assert "timestamp" in corps
    assert corps["data"] == {"statut": "ok"}


def test_creation_reunion_hippodrome_inconnu_retourne_404_normalise(client):
    reponse = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 999, "numero": 1}
    )
    assert reponse.status_code == 404
    corps = reponse.json()
    assert corps["success"] is False
    assert corps["error"]["code"] == "RESSOURCE_INTROUVABLE"


def test_creation_course_reunion_inconnue_retourne_404(client):
    reponse = client.post("/api/v1/reunions/999/courses", json={"numero": 1, "nom": "Test"})
    assert reponse.status_code == 404


def test_creation_partant_cheval_inconnu_retourne_404(client):
    reunion = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1}
    ).json()["data"]
    course = client.post(
        f"/api/v1/reunions/{reunion['id']}/courses", json={"numero": 1, "nom": "Test"}
    ).json()["data"]

    reponse = client.post(f"/api/v1/courses/{course['id']}/partants", json={"cheval_id": 999, "numero": 1})
    assert reponse.status_code == 404


def test_creation_partant_jockey_inconnu_retourne_404(client):
    reunion = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1}
    ).json()["data"]
    course = client.post(
        f"/api/v1/reunions/{reunion['id']}/courses", json={"numero": 1, "nom": "Test"}
    ).json()["data"]
    cheval = client.post("/api/v1/chevaux", json={"nom": "Cheval Test"}).json()["data"]

    reponse = client.post(
        f"/api/v1/courses/{course['id']}/partants",
        json={"cheval_id": cheval["id"], "numero": 1, "jockey_id": 999},
    )
    assert reponse.status_code == 404
    assert reponse.json()["error"]["code"] == "RESSOURCE_INTROUVABLE"


def test_creation_partant_entraineur_inconnu_retourne_404(client):
    reunion = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1}
    ).json()["data"]
    course = client.post(
        f"/api/v1/reunions/{reunion['id']}/courses", json={"numero": 1, "nom": "Test"}
    ).json()["data"]
    cheval = client.post("/api/v1/chevaux", json={"nom": "Cheval Test"}).json()["data"]

    reponse = client.post(
        f"/api/v1/courses/{course['id']}/partants",
        json={"cheval_id": cheval["id"], "numero": 1, "entraineur_id": 999},
    )
    assert reponse.status_code == 404
    assert reponse.json()["error"]["code"] == "RESSOURCE_INTROUVABLE"


def test_validation_pydantic_retourne_enveloppe_422(client):
    reponse = client.post("/api/v1/reunions", json={"hippodrome_id": 1, "numero": 1})
    assert reponse.status_code == 422
    corps = reponse.json()
    assert corps["success"] is False
    assert corps["error"]["code"] == "VALIDATION_ERROR"


def test_analyse_sur_course_inconnue_retourne_404(client):
    reponse = client.post(
        "/api/v1/courses/999/analyses",
        json={"partants": [], "sous_risques_course": {}},
    )
    assert reponse.status_code == 404
