"""Tests d'intégration des endpoints DELETE — cf. plan "Résultats/cotes en
écriture, PATCH/DELETE, authentification réelle". La contrainte FK ON DELETE
RESTRICT est simulée par FakeCourseRepository._supprimer (BusinessRuleError si des
données sont rattachées, cf. tests/integration/fakes.py), traduite en 409 par le
gestionnaire d'erreurs (cf. api/middlewares/error_handler.py).
"""


def test_delete_reunion_vide(client):
    reunion = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1}
    ).json()["data"]
    reponse = client.delete(f"/api/v1/reunions/{reunion['id']}")
    assert reponse.status_code == 200
    assert reponse.json()["data"]["supprime"] is True
    assert client.get(f"/api/v1/reunions/{reunion['id']}").status_code == 404


def test_delete_reunion_avec_course_retourne_409(client):
    reunion = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1}
    ).json()["data"]
    client.post(f"/api/v1/reunions/{reunion['id']}/courses", json={"numero": 1, "nom": "Prix Test"})

    reponse = client.delete(f"/api/v1/reunions/{reunion['id']}")
    assert reponse.status_code == 409
    assert reponse.json()["error"]["code"] == "BUSINESS_RULE_ERROR"


def test_delete_reunion_inconnue_retourne_404(client):
    assert client.delete("/api/v1/reunions/999").status_code == 404


def test_delete_course_avec_partant_retourne_409(client):
    reunion = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1}
    ).json()["data"]
    course = client.post(
        f"/api/v1/reunions/{reunion['id']}/courses", json={"numero": 1, "nom": "Prix Test"}
    ).json()["data"]
    cheval = client.post("/api/v1/chevaux", json={"nom": "Cheval Test"}).json()["data"]
    client.post(f"/api/v1/courses/{course['id']}/partants", json={"cheval_id": cheval["id"], "numero": 1})

    reponse = client.delete(f"/api/v1/courses/{course['id']}")
    assert reponse.status_code == 409


def test_delete_cheval_avec_partant_retourne_409(client):
    reunion = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1}
    ).json()["data"]
    course = client.post(
        f"/api/v1/reunions/{reunion['id']}/courses", json={"numero": 1, "nom": "Prix Test"}
    ).json()["data"]
    cheval = client.post("/api/v1/chevaux", json={"nom": "Cheval Test"}).json()["data"]
    client.post(f"/api/v1/courses/{course['id']}/partants", json={"cheval_id": cheval["id"], "numero": 1})

    reponse = client.delete(f"/api/v1/chevaux/{cheval['id']}")
    assert reponse.status_code == 409


def test_delete_cheval_sans_partant(client):
    cheval = client.post("/api/v1/chevaux", json={"nom": "Cheval Test"}).json()["data"]
    reponse = client.delete(f"/api/v1/chevaux/{cheval['id']}")
    assert reponse.status_code == 200


def test_delete_jockey_sans_partant(client):
    jockey = client.post("/api/v1/jockeys", json={"nom": "Dupont"}).json()["data"]
    assert client.delete(f"/api/v1/jockeys/{jockey['id']}").status_code == 200


def test_delete_entraineur_sans_partant(client):
    entraineur = client.post("/api/v1/entraineurs", json={"nom": "Martin"}).json()["data"]
    assert client.delete(f"/api/v1/entraineurs/{entraineur['id']}").status_code == 200


def test_delete_partant_sans_resultat_ni_cote(client):
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

    assert client.delete(f"/api/v1/partants/{partant['id']}").status_code == 200


def test_delete_partant_avec_resultat_retourne_409(client):
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
    client.post(f"/api/v1/courses/{course['id']}/resultats", json={"partant_id": partant["id"], "classement": 1})

    reponse = client.delete(f"/api/v1/partants/{partant['id']}")
    assert reponse.status_code == 409
