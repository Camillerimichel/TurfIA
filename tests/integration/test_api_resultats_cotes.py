"""Tests d'intégration des endpoints résultats/cotes en écriture — cf. plan
"Résultats/cotes en écriture, PATCH/DELETE, authentification réelle". Ces
ressources sont historisées (L011 §15) : uniquement POST + GET, jamais de
PATCH/DELETE.
"""


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
    return course, partant


def test_creation_et_lecture_resultat(client):
    course, partant = _creer_course_avec_partant(client)

    reponse = client.post(
        f"/api/v1/courses/{course['id']}/resultats",
        json={"partant_id": partant["id"], "classement": 1, "temps": "1'12\"3"},
    )
    assert reponse.status_code == 201
    resultat = reponse.json()["data"]
    assert resultat["course_id"] == course["id"]
    assert resultat["classement"] == 1

    liste = client.get(f"/api/v1/courses/{course['id']}/resultats")
    assert liste.status_code == 200
    assert len(liste.json()["data"]) == 1


def test_creation_resultat_partant_inconnu_retourne_404(client):
    course, _ = _creer_course_avec_partant(client)
    reponse = client.post(
        f"/api/v1/courses/{course['id']}/resultats", json={"partant_id": 999, "classement": 1}
    )
    assert reponse.status_code == 404


def test_creation_resultat_course_inconnue_retourne_404(client):
    reponse = client.post("/api/v1/courses/999/resultats", json={"partant_id": 1, "classement": 1})
    assert reponse.status_code == 404


def test_aucun_patch_delete_sur_resultats(client):
    course, partant = _creer_course_avec_partant(client)
    client.post(f"/api/v1/courses/{course['id']}/resultats", json={"partant_id": partant["id"], "classement": 1})
    # Seuls GET/POST sont enregistrés sur ce chemin (cf. api/routes/courses.py) :
    # PATCH/DELETE ne correspondent à aucune méthode définie -> 405.
    assert client.patch(f"/api/v1/courses/{course['id']}/resultats", json={}).status_code == 405
    assert client.delete(f"/api/v1/courses/{course['id']}/resultats").status_code == 405


def test_creation_et_lecture_cotes_historisees(client):
    _, partant = _creer_course_avec_partant(client)

    premiere = client.post(f"/api/v1/partants/{partant['id']}/cotes", json={"operateur": "PMU", "cote": 5.0})
    assert premiere.status_code == 201
    seconde = client.post(f"/api/v1/partants/{partant['id']}/cotes", json={"operateur": "PMU", "cote": 4.5})
    assert seconde.status_code == 201

    liste = client.get(f"/api/v1/partants/{partant['id']}/cotes")
    assert liste.status_code == 200
    cotes = liste.json()["data"]
    assert len(cotes) == 2  # les deux cotes sont conservées, jamais remplacées
    assert {c["cote"] for c in cotes} == {5.0, 4.5}


def test_creation_cote_partant_inconnu_retourne_404(client):
    reponse = client.post("/api/v1/partants/999/cotes", json={"operateur": "PMU", "cote": 5.0})
    assert reponse.status_code == 404


def test_aucun_patch_delete_sur_cotes(client):
    _, partant = _creer_course_avec_partant(client)
    client.post(f"/api/v1/partants/{partant['id']}/cotes", json={"operateur": "PMU", "cote": 5.0})
    assert client.patch(f"/api/v1/partants/{partant['id']}/cotes", json={}).status_code == 405
    assert client.delete(f"/api/v1/partants/{partant['id']}/cotes").status_code == 405
