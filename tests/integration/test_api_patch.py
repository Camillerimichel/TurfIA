"""Tests d'intégration des endpoints PATCH — correction partielle des ressources
mutables (cf. plan "Résultats/cotes en écriture, PATCH/DELETE, authentification
réelle"). Jamais de PATCH sur résultat/cote (historisés, vérifié dans
tests/integration/test_api_resultats_cotes.py).
"""


def test_patch_reunion_modifie_uniquement_le_statut(client):
    reunion = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1}
    ).json()["data"]

    reponse = client.patch(f"/api/v1/reunions/{reunion['id']}", json={"statut": "Terminée"})
    assert reponse.status_code == 200
    corps = reponse.json()["data"]
    assert corps["statut"] == "Terminée"
    assert corps["hippodrome_id"] == reunion["hippodrome_id"]  # inchangé


def test_patch_reunion_inconnue_retourne_404(client):
    reponse = client.patch("/api/v1/reunions/999", json={"statut": "Terminée"})
    assert reponse.status_code == 404


def test_patch_course_modifie_les_champs_fournis(client):
    reunion = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1}
    ).json()["data"]
    course = client.post(
        f"/api/v1/reunions/{reunion['id']}/courses", json={"numero": 1, "nom": "Prix Test"}
    ).json()["data"]

    reponse = client.patch(f"/api/v1/courses/{course['id']}", json={"allocation": 50000.0})
    assert reponse.status_code == 200
    corps = reponse.json()["data"]
    assert corps["allocation"] == 50000.0
    assert corps["nom"] == "Prix Test"  # inchangé


def test_patch_cheval_toggle_actif(client):
    cheval = client.post("/api/v1/chevaux", json={"nom": "Cheval Test"}).json()["data"]
    reponse = client.patch(f"/api/v1/chevaux/{cheval['id']}", json={"actif": False})
    assert reponse.status_code == 200
    assert reponse.json()["data"]["actif"] is False


def test_patch_jockey_corrige_le_nom(client):
    jockey = client.post("/api/v1/jockeys", json={"nom": "Dupont"}).json()["data"]
    reponse = client.patch(f"/api/v1/jockeys/{jockey['id']}", json={"nom": "Dupond"})
    assert reponse.status_code == 200
    assert reponse.json()["data"]["nom"] == "Dupond"


def test_patch_entraineur_toggle_actif(client):
    entraineur = client.post("/api/v1/entraineurs", json={"nom": "Martin"}).json()["data"]
    reponse = client.patch(f"/api/v1/entraineurs/{entraineur['id']}", json={"actif": False})
    assert reponse.status_code == 200
    assert reponse.json()["data"]["actif"] is False


def _creer_course_avec_partant(client):
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
    return partant


def test_patch_partant_non_partant(client):
    partant = _creer_course_avec_partant(client)
    reponse = client.patch(f"/api/v1/partants/{partant['id']}", json={"non_partant": True})
    assert reponse.status_code == 200
    assert reponse.json()["data"]["non_partant"] is True


def test_get_partant_isole(client):
    partant = _creer_course_avec_partant(client)
    reponse = client.get(f"/api/v1/partants/{partant['id']}")
    assert reponse.status_code == 200
    assert reponse.json()["data"]["id"] == partant["id"]


def test_patch_partant_jockey_inconnu_retourne_404(client):
    partant = _creer_course_avec_partant(client)
    reponse = client.patch(f"/api/v1/partants/{partant['id']}", json={"jockey_id": 999})
    assert reponse.status_code == 404


def test_patch_partant_inconnu_retourne_404(client):
    reponse = client.patch("/api/v1/partants/999", json={"non_partant": True})
    assert reponse.status_code == 404
