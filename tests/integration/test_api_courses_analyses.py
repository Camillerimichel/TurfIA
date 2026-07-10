"""Tests d'intégration API — cf. L020 §5 (API <-> Services), sans base réelle
(repositories simulés, cf. tests/integration/fakes.py).
"""

from src.models.referentiels import Hippodrome


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


def test_creation_et_lecture_cheval(client):
    cheval = client.post("/api/v1/chevaux", json={"nom": "Cheval Test"}).json()["data"]
    reponse = client.get(f"/api/v1/chevaux/{cheval['id']}")
    assert reponse.status_code == 200
    assert reponse.json()["data"]["nom"] == "Cheval Test"


def test_lecture_cheval_inconnu_retourne_404(client):
    reponse = client.get("/api/v1/chevaux/999")
    assert reponse.status_code == 404


def test_creation_et_lecture_jockey(client):
    jockey = client.post("/api/v1/jockeys", json={"nom": "Dupont", "prenom": "Jean"}).json()["data"]
    reponse = client.get(f"/api/v1/jockeys/{jockey['id']}")
    assert reponse.status_code == 200
    corps = reponse.json()["data"]
    assert corps["nom"] == "Dupont"
    assert corps["prenom"] == "Jean"
    assert corps["actif"] is True


def test_lecture_jockey_inconnu_retourne_404(client):
    reponse = client.get("/api/v1/jockeys/999")
    assert reponse.status_code == 404


def test_creation_et_lecture_entraineur(client):
    entraineur = client.post("/api/v1/entraineurs", json={"nom": "Martin"}).json()["data"]
    reponse = client.get(f"/api/v1/entraineurs/{entraineur['id']}")
    assert reponse.status_code == 200
    assert reponse.json()["data"]["nom"] == "Martin"


def test_lecture_entraineur_inconnu_retourne_404(client):
    reponse = client.get("/api/v1/entraineurs/999")
    assert reponse.status_code == 404


def test_creation_partant_avec_jockey_et_entraineur_connus(client):
    reunion = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1}
    ).json()["data"]
    course = client.post(
        f"/api/v1/reunions/{reunion['id']}/courses", json={"numero": 1, "nom": "Test"}
    ).json()["data"]
    cheval = client.post("/api/v1/chevaux", json={"nom": "Cheval Test"}).json()["data"]
    jockey = client.post("/api/v1/jockeys", json={"nom": "Dupont"}).json()["data"]
    entraineur = client.post("/api/v1/entraineurs", json={"nom": "Martin"}).json()["data"]

    reponse = client.post(
        f"/api/v1/courses/{course['id']}/partants",
        json={
            "cheval_id": cheval["id"],
            "numero": 1,
            "jockey_id": jockey["id"],
            "entraineur_id": entraineur["id"],
        },
    )
    assert reponse.status_code == 201
    corps = reponse.json()["data"]
    assert corps["jockey_id"] == jockey["id"]
    assert corps["entraineur_id"] == entraineur["id"]


def test_list_partants_expose_noms_et_derniere_cote_par_jointure(client):
    """cf. CourseRepository.list_partants_detail_by_course — remplace les
    appels N+1 (GET /chevaux/{id}, /jockeys/{id}, /entraineurs/{id},
    /partants/{id}/cotes) faits jusqu'ici par la fiche course HTML."""
    reunion = client.post(
        "/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1}
    ).json()["data"]
    course = client.post(
        f"/api/v1/reunions/{reunion['id']}/courses", json={"numero": 1, "nom": "Test"}
    ).json()["data"]
    cheval = client.post("/api/v1/chevaux", json={"nom": "Cheval Test"}).json()["data"]
    jockey = client.post("/api/v1/jockeys", json={"nom": "Dupont", "prenom": "Jean"}).json()["data"]
    entraineur = client.post("/api/v1/entraineurs", json={"nom": "Martin"}).json()["data"]
    partant = client.post(
        f"/api/v1/courses/{course['id']}/partants",
        json={"cheval_id": cheval["id"], "numero": 1, "jockey_id": jockey["id"], "entraineur_id": entraineur["id"]},
    ).json()["data"]
    client.post(f"/api/v1/partants/{partant['id']}/cotes", json={"operateur": "PMU", "cote": 4.5})

    reponse = client.get(f"/api/v1/courses/{course['id']}/partants")

    assert reponse.status_code == 200
    corps = reponse.json()["data"][0]
    assert corps["cheval_nom"] == "Cheval Test"
    assert corps["jockey_nom"] == "Dupont"
    assert corps["jockey_prenom"] == "Jean"
    assert corps["entraineur_nom"] == "Martin"
    assert corps["derniere_cote"] == 4.5
    assert corps["derniere_cote_operateur"] == "PMU"


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


def test_list_reunions_par_date(client):
    client.post("/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1})
    client.post("/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 2})
    client.post("/api/v1/reunions", json={"date": "2026-07-08", "hippodrome_id": 1, "numero": 1})

    reponse = client.get("/api/v1/reunions", params={"date": "2026-07-07"})
    assert reponse.status_code == 200
    corps = reponse.json()["data"]
    assert len(corps) == 2
    assert [r["numero"] for r in corps] == [1, 2]
    assert corps[0]["hippodrome_nom"] == "ParisLongchamp"


def test_list_reunions_filtre_par_hippodrome(client, repos):
    autre_hippodrome = repos["referentiel"].seed_hippodrome(Hippodrome(nom="Vincennes", ville="Paris", pays="France"))
    client.post("/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": 1, "numero": 1})
    client.post("/api/v1/reunions", json={"date": "2026-07-07", "hippodrome_id": autre_hippodrome.id, "numero": 1})

    reponse = client.get("/api/v1/reunions", params={"date": "2026-07-07", "hippodrome_id": autre_hippodrome.id})

    assert reponse.status_code == 200
    corps = reponse.json()["data"]
    assert len(corps) == 1
    assert corps[0]["hippodrome_nom"] == "Vincennes"


def test_list_reunions_date_sans_reunion_est_vide(client):
    reponse = client.get("/api/v1/reunions", params={"date": "2026-01-01"})
    assert reponse.status_code == 200
    assert reponse.json()["data"] == []


def test_list_reunions_sans_date_utilise_aujourdhui(client):
    reponse = client.get("/api/v1/reunions")
    assert reponse.status_code == 200
    assert reponse.json()["data"] == []
